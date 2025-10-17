from __future__ import annotations

from collections import defaultdict, deque
from datetime import date, time
from typing import Iterable

from sqlalchemy.orm import Session

from ..config import settings
from ..models import (
    DayPlan,
    Edge,
    EventLog,
    FailureStats,
    Habit,
    NodeType,
    PlanAnchor,
    PlanItem,
    PlanStatus,
    RelationType,
    Task,
    User,
)

# Tunables for heuristics
DEFAULT_MORNING_WINDOW = (6, 11)
DEFAULT_AFTERNOON_WINDOW = (11, 17)
DEFAULT_EVENING_WINDOW = (17, 22)


def _time_to_minutes(value: time | None) -> int:
    if value is None:
        return 24 * 60
    return value.hour * 60 + value.minute


def _preferred_window(energy_tag: str | None) -> tuple[int, int]:
    if not energy_tag:
        return DEFAULT_AFTERNOON_WINDOW
    tag = energy_tag.lower()
    if "morning" in tag:
        return DEFAULT_MORNING_WINDOW
    if "evening" in tag or "night" in tag:
        return DEFAULT_EVENING_WINDOW
    return DEFAULT_AFTERNOON_WINDOW


def _determine_energy_window(db: Session, user_id: int) -> tuple[int, int]:
    """Derive high-energy window from events or fallback settings."""
    # TODO: derive from EventLog analytics.
    return settings.scheduler_high_energy_window


def _ensure_day_plan(db: Session, user_id: int, target_date: date) -> DayPlan:
    plan = (
        db.query(DayPlan).filter(DayPlan.user_id == user_id, DayPlan.date == target_date).first()
    )
    if plan:
        plan.items.clear()
        return plan

    plan = DayPlan(user_id=user_id, date=target_date)
    db.add(plan)
    return plan


def _collect_nodes(
    habits: Iterable[Habit], tasks: Iterable[Task]
) -> dict[tuple[NodeType, int], dict]:
    nodes: dict[tuple[NodeType, int], dict] = {}
    for habit in habits:
        nodes[(NodeType.HABIT, habit.id)] = {
            "obj": habit,
            "soft_start": habit.soft_window_start,
            "soft_end": habit.soft_window_end,
            "energy_tag": habit.energy_tag,
        }

    for task in tasks:
        nodes[(NodeType.TASK, task.id)] = {
            "obj": task,
            "soft_start": getattr(task.habit, "soft_window_start", None),
            "soft_end": getattr(task.habit, "soft_window_end", None),
            "energy_tag": task.energy_tag or getattr(task.habit, "energy_tag", None),
        }
    return nodes


def _build_dependency_graph(edges: Iterable[Edge]) -> tuple[dict[tuple[NodeType, int], set], dict[tuple[NodeType, int], int]]:
    adjacency: dict[tuple[NodeType, int], set] = defaultdict(set)
    indegree: dict[tuple[NodeType, int], int] = defaultdict(int)

    for edge in edges:
        key_from = (edge.from_type, edge.from_id)
        key_to = (edge.to_type, edge.to_id)

        if edge.relation in {RelationType.TRIGGERS, RelationType.FOLLOWS, RelationType.SUPPORTS}:
            adjacency[key_from].add(key_to)
            indegree[key_to] += 1
            indegree.setdefault(key_from, 0)

    return adjacency, indegree


def generate_day_plan(db: Session, user_id: int, target_date: date) -> DayPlan:
    """Generate or refresh the day plan for the given user/date."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    tasks = db.query(Task).filter(Task.user_id == user_id, Task.active.is_(True)).all()
    edges = db.query(Edge).filter(Edge.user_id == user_id).all()

    nodes = _collect_nodes(habits, tasks)
    adjacency, indegree = _build_dependency_graph(edges)

    # Ensure nodes exist in indegree even if no edges.
    for key in nodes:
        indegree.setdefault(key, 0)

    initial_ready = {
        key for key, degree in indegree.items() if degree == 0 and key in nodes
    }

    processing_queue = deque(
        sorted(
            [key for key, degree in indegree.items() if degree == 0],
            key=lambda node_key: _time_to_minutes(nodes.get(node_key, {}).get("soft_start")),
        )
    )

    order: list[tuple[NodeType, int]] = []
    while processing_queue:
        node_key = processing_queue.popleft()
        order.append(node_key)
        for neighbour in adjacency.get(node_key, []):
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                processing_queue.append(neighbour)
        processing_queue = deque(
            sorted(
                processing_queue,
                key=lambda key: _time_to_minutes(nodes.get(key, {}).get("soft_start")),
            )
        )

    # Fallback for cycles: append remaining nodes in arbitrary order.
    remaining = [key for key, degree in indegree.items() if degree > 0]
    for rem in remaining:
        if rem not in order:
            order.append(rem)

    plan = _ensure_day_plan(db, user_id, target_date)
    high_energy_start, high_energy_end = _determine_energy_window(db, user_id)

    plan.items.clear()
    for idx, (node_type, node_id) in enumerate(order, start=1):
        node_info = nodes.get((node_type, node_id))
        soft_start = node_info.get("soft_start") if node_info else None
        soft_end = node_info.get("soft_end") if node_info else None
        energy_tag = node_info.get("energy_tag") if node_info else None

        anchor = PlanAnchor.TIME if soft_start or soft_end else None

        # Heuristic: if item energy matches high energy window, prefer earlier order.
        if energy_tag and "high" in energy_tag.lower():
            if high_energy_start <= 10:  # simple tweak; TODO more nuance
                soft_start = soft_start or time(hour=high_energy_start)
                soft_end = soft_end or time(hour=high_energy_end)

        plan.items.append(
            PlanItem(
                node_type=node_type,
                node_id=node_id,
                status=PlanStatus.READY if (node_type, node_id) in initial_ready else PlanStatus.PLANNED,
                scheduled_order=idx,
                scheduled_window_start=soft_start,
                scheduled_window_end=soft_end,
                anchor=anchor,
            )
        )

    db.commit()
    db.refresh(plan)
    return plan

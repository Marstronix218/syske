from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import (
    DayPlan,
    EventLog,
    Gamification,
    PlanAnchor,
    PlanItem,
    PlanStatus,
)


def compute_points(
    plan_item: PlanItem,
    completion_time: datetime,
    *,
    previous_completion: datetime | None,
    anchor_completed_at: datetime | None,
) -> int:
    points = 0
    if plan_item.status == PlanStatus.DONE:
        if plan_item.scheduled_window_start and plan_item.scheduled_window_end:
            window_start = completion_time.replace(
                hour=plan_item.scheduled_window_start.hour,
                minute=plan_item.scheduled_window_start.minute,
            )
            window_end = completion_time.replace(
                hour=plan_item.scheduled_window_end.hour,
                minute=plan_item.scheduled_window_end.minute,
            )
            if window_start <= completion_time <= window_end:
                points += 5
            else:
                points += 2
        else:
            points += 3

        if previous_completion and completion_time - previous_completion <= timedelta(minutes=60):
            points += 2

        if anchor_completed_at and completion_time - anchor_completed_at <= timedelta(minutes=60):
            points += 3
    elif plan_item.status == PlanStatus.SKIPPED:
        points -= 2
    return points


def update_flow_score(db: Session, day_plan: DayPlan) -> None:
    """Recompute flow score and update gamification tracker."""
    plan_items = (
        db.query(PlanItem)
        .filter(PlanItem.dayplan_id == day_plan.id)
        .order_by(PlanItem.scheduled_order.asc())
        .all()
    )

    last_completion: datetime | None = None
    anchor_completion: dict[int, datetime] = {}
    score = 0

    events = (
        db.query(EventLog)
        .filter(
            EventLog.user_id == day_plan.user_id,
            EventLog.event_type.in_(["plan_complete", "plan_skip"]),
        )
        .all()
    )
    events_by_plan_item: dict[int, list[EventLog]] = {}
    for evt in events:
        payload = evt.payload_json or {}
        plan_item_id = payload.get("plan_item_id")
        if plan_item_id:
            events_by_plan_item.setdefault(plan_item_id, []).append(evt)

    for item in plan_items:
        item_events = sorted(events_by_plan_item.get(item.id, []), key=lambda evt: evt.ts)
        completion_event = next((evt for evt in item_events if evt.event_type == "plan_complete"), None)
        anchor_completed_at = (
            anchor_completion.get(item.node_id) if item.anchor in {PlanAnchor.HABIT, PlanAnchor.TASK} else None
        )

        completed_at = completion_event.ts if completion_event else None
        points = compute_points(
            item,
            completed_at or datetime.utcnow(),
            previous_completion=last_completion,
            anchor_completed_at=anchor_completed_at,
        )
        score += points
        if item.status == PlanStatus.DONE and completed_at:
            last_completion = completed_at
            anchor_completion[item.node_id] = completed_at

    day_plan.flow_score = score
    gamification = (
        db.query(Gamification)
        .filter(Gamification.user_id == day_plan.user_id, Gamification.date == day_plan.date)
        .first()
    )
    if not gamification:
        gamification = Gamification(
            user_id=day_plan.user_id,
            date=day_plan.date,
            streak_days=0,
            xp=0,
            flow_streak=0,
        )
        db.add(gamification)

    if score > 0:
        gamification.xp += score
        if score >= 10:
            gamification.flow_streak += 1
    else:
        gamification.flow_streak = 0

    db.commit()

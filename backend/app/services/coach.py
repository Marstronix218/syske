from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from ..config import settings
from ..models import EventLog, FailureStats, Habit, NodeType, Task
from ..schemas import CoachSuggestion, CoachSuggestionAction


def _lookup_node(db: Session, node_type: NodeType, node_id: int):
    if node_type == NodeType.HABIT:
        return db.query(Habit).filter(Habit.id == node_id).first()
    if node_type == NodeType.TASK:
        return db.query(Task).filter(Task.id == node_id).first()
    return None


def suggest_fixes(db: Session, user_id: int, node_type: NodeType, node_id: int) -> CoachSuggestion:
    stats = (
        db.query(FailureStats)
        .filter(
            FailureStats.user_id == user_id,
            FailureStats.node_type == node_type,
            FailureStats.node_id == node_id,
        )
        .first()
    )
    node = _lookup_node(db, node_type, node_id)

    actions: list[CoachSuggestionAction] = []
    if stats and stats.rolling_fail_count >= settings.fail_threshold:
        label = getattr(node, "name", None) or getattr(node, "title", "item")
        actions.append(
            CoachSuggestionAction(
                title="Shrink the scope",
                description=f"Try a smaller version of {label}. Cut the expected time or difficulty for a quick win.",
                suggestion_type="reduce_scope",
            )
        )
        actions.append(
            CoachSuggestionAction(
                title="Adjust the sequence",
                description="Move this step to when you have more energy or pair it with a habit you already complete.",
                suggestion_type="swap_order",
            )
        )
        actions.append(
            CoachSuggestionAction(
                title="Add a band-aid step",
                description="Add a tiny prep action (open materials, set a 5-minute timer) to lower friction.",
                suggestion_type="band_aid",
            )
        )
        if node_type == NodeType.HABIT:
            actions.append(
                CoachSuggestionAction(
                    title="Automate or delegate",
                    description="Consider reminders, automations, or asking for help to keep the habit alive.",
                    suggestion_type="automate",
                )
            )
    else:
        actions.append(
            CoachSuggestionAction(
                title="Stay curious",
                description="You are experimenting with your system. Keep notes on what works and adjust soon.",
                suggestion_type="encourage",
            )
        )

    suggestion = CoachSuggestion(node_type=node_type, node_id=node_id, actions=actions)
    db.add(
        EventLog(
            user_id=user_id,
            ts=datetime.utcnow(),
            event_type="coach_suggest",
            payload_json=suggestion.model_dump(),
        )
    )
    db.commit()
    return suggestion

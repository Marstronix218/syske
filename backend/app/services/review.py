from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import DayPlan, EventLog, PlanItem, PlanStatus, Review, ReviewType
from ..schemas import CoachSuggestionAction, ReviewSummary
from . import coach


def generate_daily_summary(db: Session, user_id: int, target_date: date) -> ReviewSummary:
    plan = (
        db.query(DayPlan)
        .filter(DayPlan.user_id == user_id, DayPlan.date == target_date)
        .first()
    )
    if not plan:
        raise ValueError("No plan found for date")

    total = len(plan.items)
    done = len([item for item in plan.items if item.status == PlanStatus.DONE])
    skipped = len([item for item in plan.items if item.status == PlanStatus.SKIPPED])
    completion_rate = done / total if total else 0.0

    tweaks: list[CoachSuggestionAction] = []
    if skipped:
        # Identify most recent skipped node for coaching.
        last_skipped: Optional[PlanItem] = (
            db.query(PlanItem)
            .filter(
                PlanItem.dayplan_id == plan.id,
                PlanItem.status == PlanStatus.SKIPPED,
            )
            .order_by(PlanItem.id.desc())
            .first()
        )
        if last_skipped:
            suggestion = coach.suggest_fixes(db, user_id, last_skipped.node_type, last_skipped.node_id)
            tweaks.extend(suggestion.actions[:3])

    summary = (
        f"{int(completion_rate * 100)}% complete. "
        f"Flow score {plan.flow_score}. "
        "Notice skips? Reflect on energy and sequence alignment."
    )

    db.add(
        Review(
            user_id=user_id,
            date_range_start=target_date,
            date_range_end=target_date,
            type=ReviewType.DAILY,
            reflection_text=None,
            ai_summary=summary,
            ai_suggestions_json={"tweaks": [action.model_dump() for action in tweaks]},
        )
    )
    db.commit()

    return ReviewSummary(
        summary=summary,
        tweaks=tweaks,
        completion_rate=completion_rate,
        flow_score=plan.flow_score,
    )


def generate_weekly_summary(db: Session, user_id: int, ending_date: date) -> ReviewSummary:
    start_date = ending_date - timedelta(days=6)
    plans = (
        db.query(DayPlan)
        .filter(
            DayPlan.user_id == user_id,
            DayPlan.date >= start_date,
            DayPlan.date <= ending_date,
        )
        .all()
    )
    total_items = 0
    total_done = 0
    aggregate_flow = 0
    for plan in plans:
        total_items += len(plan.items)
        total_done += len([item for item in plan.items if item.status == PlanStatus.DONE])
        aggregate_flow += plan.flow_score

    completion_rate = total_done / total_items if total_items else 0.0
    average_flow = int(aggregate_flow / len(plans)) if plans else 0

    tweaks: list[CoachSuggestionAction] = []
    # Identify nodes with most skips in the week.
    skipped_counts = (
        db.query(PlanItem.node_type, PlanItem.node_id, func.count(PlanItem.id))
        .join(DayPlan)
        .filter(
            DayPlan.user_id == user_id,
            DayPlan.date >= start_date,
            DayPlan.date <= ending_date,
            PlanItem.status == PlanStatus.SKIPPED,
        )
        .group_by(PlanItem.node_type, PlanItem.node_id)
        .order_by(func.count(PlanItem.id).desc())
        .limit(2)
        .all()
    )

    for node_type, node_id, _ in skipped_counts:
        suggestion = coach.suggest_fixes(db, user_id, node_type, node_id)
        tweaks.extend(suggestion.actions[:2])

    summary = (
        f"Weekly completion: {int(completion_rate * 100)}%. "
        f"Average flow score: {average_flow}. "
        "Trends: double-down on high-flow windows and redesign the frequent skips."
    )

    db.add(
        Review(
            user_id=user_id,
            date_range_start=start_date,
            date_range_end=ending_date,
            type=ReviewType.WEEKLY,
            reflection_text=None,
            ai_summary=summary,
            ai_suggestions_json={"tweaks": [action.model_dump() for action in tweaks]},
        )
    )
    db.commit()

    return ReviewSummary(
        summary=summary,
        tweaks=tweaks,
        completion_rate=completion_rate,
        flow_score=average_flow,
    )

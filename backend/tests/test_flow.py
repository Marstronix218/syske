from datetime import date, datetime, time

from app.models import DayPlan, EventLog, NodeType, PlanItem, PlanStatus
from app.services import flow


def test_flow_score_rewards_window_completion(in_memory_db):
    dayplan = DayPlan(user_id=1, date=date.today())
    in_memory_db.add(dayplan)
    in_memory_db.flush()

    item = PlanItem(
        dayplan_id=dayplan.id,
        node_type=NodeType.HABIT,
        node_id=1,
        status=PlanStatus.DONE,
        scheduled_order=1,
        scheduled_window_start=time(hour=9),
        scheduled_window_end=time(hour=10),
    )
    in_memory_db.add(item)
    in_memory_db.flush()

    in_memory_db.add(
        EventLog(
            user_id=dayplan.user_id,
            ts=datetime.utcnow().replace(hour=9, minute=30),
            event_type="plan_complete",
            payload_json={"plan_item_id": item.id},
        )
    )
    in_memory_db.commit()

    flow.update_flow_score(in_memory_db, dayplan)
    in_memory_db.refresh(dayplan)
    assert dayplan.flow_score >= 5

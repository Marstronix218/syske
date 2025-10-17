from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import DayPlan, Edge, EventLog, FailureStats, PlanItem, PlanStatus
from ...schemas import (
    DayPlan as DayPlanSchema,
    PlanCompleteRequest,
    PlanGenerateResponse,
    PlanSkipRequest,
)
from ...services import flow, scheduler

router = APIRouter()


@router.get("", response_model=DayPlanSchema)
def get_plan(user_id: int = Query(...), plan_date: date = Query(...), db: Session = Depends(get_db)):
    plan = (
        db.query(DayPlan)
        .filter(DayPlan.user_id == user_id, DayPlan.date == plan_date)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return DayPlanSchema.model_validate(plan)


@router.post("/generate", response_model=PlanGenerateResponse)
def generate_plan(user_id: int = Query(...), plan_date: date = Query(...), db: Session = Depends(get_db)):
    plan = scheduler.generate_day_plan(db, user_id=user_id, target_date=plan_date)
    return PlanGenerateResponse(plan=DayPlanSchema.model_validate(plan))


@router.post("/complete")
def complete_plan_item(
    payload: PlanCompleteRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    plan_item = (
        db.query(PlanItem)
        .join(DayPlan)
        .filter(
            PlanItem.id == payload.plan_item_id,
            DayPlan.user_id == user_id,
        )
        .first()
    )
    if not plan_item:
        raise HTTPException(status_code=404, detail="Plan item not found")

    plan_item.status = PlanStatus.DONE
    completion_ts = payload.ts or datetime.utcnow()

    db.add(
        EventLog(
            user_id=user_id,
            ts=completion_ts,
            event_type="plan_complete",
            payload_json={
                "plan_item_id": plan_item.id,
                "node_type": plan_item.node_type,
                "node_id": plan_item.node_id,
            },
        )
    )

    # Reset failure stats on completion
    failure = (
        db.query(FailureStats)
        .filter(
            FailureStats.user_id == user_id,
            FailureStats.node_type == plan_item.node_type,
            FailureStats.node_id == plan_item.node_id,
        )
        .first()
    )
    if failure:
        failure.rolling_fail_count = 0
        failure.last_failed_at = None

    # Unlock dependent items
    dependents = (
        db.query(Edge)
        .filter(
            Edge.user_id == user_id,
            Edge.from_type == plan_item.node_type,
            Edge.from_id == plan_item.node_id,
        )
        .all()
    )
    db.flush()
    db.refresh(plan_item.dayplan)
    for edge in dependents:
        dependent = next(
            (
                item
                for item in plan_item.dayplan.items
                if item.node_type == edge.to_type and item.node_id == edge.to_id
            ),
            None,
        )
        if dependent and dependent.status == PlanStatus.PLANNED:
            dependent.status = PlanStatus.READY

    db.commit()
    flow.update_flow_score(db, plan_item.dayplan)
    return {"status": "ok"}


@router.post("/skip")
def skip_plan_item(
    payload: PlanSkipRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    plan_item = (
        db.query(PlanItem)
        .join(DayPlan)
        .filter(
            PlanItem.id == payload.plan_item_id,
            DayPlan.user_id == user_id,
        )
        .first()
    )
    if not plan_item:
        raise HTTPException(status_code=404, detail="Plan item not found")

    plan_item.status = PlanStatus.SKIPPED
    db.add(
        EventLog(
            user_id=user_id,
            ts=datetime.utcnow(),
            event_type="plan_skip",
            payload_json={
                "plan_item_id": plan_item.id,
                "node_type": plan_item.node_type,
                "node_id": plan_item.node_id,
                "reason": payload.reason,
            },
        )
    )

    failure = (
        db.query(FailureStats)
        .filter(
            FailureStats.user_id == user_id,
            FailureStats.node_type == plan_item.node_type,
            FailureStats.node_id == plan_item.node_id,
        )
        .first()
    )
    if not failure:
        failure = FailureStats(
            user_id=user_id,
            node_type=plan_item.node_type,
            node_id=plan_item.node_id,
            rolling_fail_count=1,
        )
        db.add(failure)
    else:
        failure.rolling_fail_count += 1
        failure.last_failed_at = datetime.utcnow()

    db.commit()
    flow.update_flow_score(db, plan_item.dayplan)
    return {"status": "ok"}

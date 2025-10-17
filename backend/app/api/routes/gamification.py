from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Gamification as GamificationModel
from ...schemas import Gamification as GamificationSchema

router = APIRouter()


@router.get("/today", response_model=GamificationSchema)
def get_today(
    user_id: int = Query(...),
    target_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
) -> GamificationSchema:
    gamification = (
        db.query(GamificationModel)
        .filter(GamificationModel.user_id == user_id, GamificationModel.date == target_date)
        .first()
    )
    if not gamification:
        gamification = GamificationModel(
            user_id=user_id,
            date=target_date,
            streak_days=0,
            xp=0,
            flow_streak=0,
        )
        db.add(gamification)
        db.commit()
        db.refresh(gamification)
    return GamificationSchema.model_validate(gamification)

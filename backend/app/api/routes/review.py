from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas import ReviewSummary
from ...services import review

router = APIRouter()


@router.get("/daily", response_model=ReviewSummary)
def get_daily_review(
    user_id: int = Query(...),
    target_date: date = Query(...),
    db: Session = Depends(get_db),
) -> ReviewSummary:
    return review.generate_daily_summary(db, user_id=user_id, target_date=target_date)


@router.get("/weekly", response_model=ReviewSummary)
def get_weekly_review(
    user_id: int = Query(...),
    ending_date: date = Query(...),
    db: Session = Depends(get_db),
) -> ReviewSummary:
    return review.generate_weekly_summary(db, user_id=user_id, ending_date=ending_date)

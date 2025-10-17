from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas import CoachRequest, CoachSuggestion
from ...services import coach

router = APIRouter()


@router.post("/suggest", response_model=CoachSuggestion)
def suggest(payload: CoachRequest, db: Session = Depends(get_db)) -> CoachSuggestion:
    return coach.suggest_fixes(
        db,
        user_id=payload.user_id,
        node_type=payload.node_type,
        node_id=payload.node_id,
    )

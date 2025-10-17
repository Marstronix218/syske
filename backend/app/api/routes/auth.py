from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import User
from ...schemas import User as UserSchema, UserCreate

router = APIRouter()


@router.post("/devlogin", response_model=UserSchema)
def dev_login(payload: UserCreate | None = None, db: Session = Depends(get_db)) -> UserSchema:
    """Development-only login that ensures a user record exists."""
    tz = payload.tz if payload else "America/Argentina/Buenos_Aires"
    user = db.query(User).filter(User.tz == tz).first()
    if not user:
        user = User(tz=tz)
        db.add(user)
        db.commit()
        db.refresh(user)
    return UserSchema.model_validate(user)

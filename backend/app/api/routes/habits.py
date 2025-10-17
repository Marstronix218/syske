from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Habit
from ...schemas import Habit as HabitSchema, HabitCreate

router = APIRouter()


@router.get("/{user_id}", response_model=list[HabitSchema])
def list_habits(user_id: int, db: Session = Depends(get_db)) -> list[HabitSchema]:
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    return [HabitSchema.model_validate(habit) for habit in habits]


@router.post("", response_model=HabitSchema)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db)) -> HabitSchema:
    habit = Habit(**payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return HabitSchema.model_validate(habit)


@router.put("/{habit_id}", response_model=HabitSchema)
def update_habit(habit_id: int, payload: HabitCreate, db: Session = Depends(get_db)) -> HabitSchema:
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    for key, value in payload.model_dump().items():
        setattr(habit, key, value)
    db.commit()
    db.refresh(habit)
    return HabitSchema.model_validate(habit)


@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    return {"status": "ok"}

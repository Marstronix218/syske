from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Task
from ...schemas import Task as TaskSchema, TaskCreate, TaskUpdate

router = APIRouter()


@router.get("/{user_id}", response_model=list[TaskSchema])
def list_tasks(user_id: int, db: Session = Depends(get_db)) -> list[TaskSchema]:
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return [TaskSchema.model_validate(task) for task in tasks]


@router.post("", response_model=TaskSchema)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskSchema:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskSchema.model_validate(task)


@router.put("/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskSchema:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return TaskSchema.model_validate(task)


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "ok"}

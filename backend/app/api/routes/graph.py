from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Edge, Goal, Habit, NodeType, System, Task, User
from ...schemas import Edge as EdgeSchema, GraphNode, GraphResponse

router = APIRouter()


@router.get("", response_model=GraphResponse)
def get_graph(user_id: int = Query(...), db: Session = Depends(get_db)) -> GraphResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    nodes: list[GraphNode] = []

    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    systems = db.query(System).filter(System.user_id == user_id).all()
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    tasks = db.query(Task).filter(Task.user_id == user_id).all()

    for goal in goals:
        nodes.append(GraphNode(id=goal.id, type=NodeType.GOAL, label=goal.title))
    for system in systems:
        nodes.append(GraphNode(id=system.id, type=NodeType.SYSTEM, label=system.title))
    for habit in habits:
        nodes.append(GraphNode(id=habit.id, type=NodeType.HABIT, label=habit.name))
    for task in tasks:
        nodes.append(GraphNode(id=task.id, type=NodeType.TASK, label=task.title))

    edges = db.query(Edge).filter(Edge.user_id == user_id).all()

    return GraphResponse(nodes=nodes, edges=[EdgeSchema.model_validate(edge) for edge in edges])

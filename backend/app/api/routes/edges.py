from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Edge
from ...schemas import Edge as EdgeSchema, EdgeCreate

router = APIRouter()


@router.get("/{user_id}", response_model=list[EdgeSchema])
def list_edges(user_id: int, db: Session = Depends(get_db)) -> list[EdgeSchema]:
    edges = db.query(Edge).filter(Edge.user_id == user_id).all()
    return [EdgeSchema.model_validate(edge) for edge in edges]


@router.post("", response_model=EdgeSchema)
def create_edge(payload: EdgeCreate, db: Session = Depends(get_db)) -> EdgeSchema:
    edge = Edge(**payload.model_dump())
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return EdgeSchema.model_validate(edge)


@router.delete("/{edge_id}")
def delete_edge(edge_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    edge = db.query(Edge).filter(Edge.id == edge_id).first()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    db.delete(edge)
    db.commit()
    return {"status": "ok"}

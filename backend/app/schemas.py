from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from .models import NodeType, PlanAnchor, PlanStatus, RelationType, ReviewType


class UserBase(BaseModel):
    tz: str = "America/Argentina/Buenos_Aires"


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None


class GoalCreate(GoalBase):
    user_id: int


class Goal(GoalBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class SystemBase(BaseModel):
    goal_id: int
    title: str
    description: Optional[str] = None


class SystemCreate(SystemBase):
    user_id: int


class System(SystemBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class HabitBase(BaseModel):
    system_id: int
    name: str
    soft_window_start: Optional[time] = None
    soft_window_end: Optional[time] = None
    energy_tag: Optional[str] = None
    recurrence_rule: Optional[str] = None
    anchor_event: Optional[str] = None


class HabitCreate(HabitBase):
    user_id: int


class Habit(HabitBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    habit_id: Optional[int] = None
    title: str
    difficulty: int = Field(ge=1, le=5, default=3)
    est_minutes: Optional[int] = None
    priority: int = Field(ge=0, default=1)
    energy_tag: Optional[str] = None
    is_recurring: bool = False
    active: bool = True


class TaskCreate(TaskBase):
    user_id: int


class Task(TaskBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    habit_id: Optional[int] = None
    title: Optional[str] = None
    difficulty: Optional[int] = Field(default=None, ge=1, le=5)
    est_minutes: Optional[int] = None
    priority: Optional[int] = None
    energy_tag: Optional[str] = None
    is_recurring: Optional[bool] = None
    active: Optional[bool] = None


class EdgeBase(BaseModel):
    from_type: NodeType
    from_id: int
    to_type: NodeType
    to_id: int
    relation: RelationType


class EdgeCreate(EdgeBase):
    user_id: int


class Edge(EdgeBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PlanItemBase(BaseModel):
    node_type: NodeType
    node_id: int
    status: PlanStatus = PlanStatus.PLANNED
    scheduled_order: Optional[int] = None
    scheduled_window_start: Optional[time] = None
    scheduled_window_end: Optional[time] = None
    anchor: Optional[PlanAnchor] = None


class PlanItem(PlanItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DayPlanBase(BaseModel):
    date: date
    flow_score: int = 0
    notes: Optional[str] = None


class DayPlan(DayPlanBase):
    id: int
    user_id: int
    generated_at: datetime
    items: list[PlanItem] = []

    model_config = ConfigDict(from_attributes=True)


class PlanGenerateResponse(BaseModel):
    plan: DayPlan


class PlanCompleteRequest(BaseModel):
    plan_item_id: int
    ts: Optional[datetime] = None


class PlanSkipRequest(BaseModel):
    plan_item_id: int
    reason: Optional[str] = None


class ReviewBase(BaseModel):
    date_range_start: date
    date_range_end: date
    type: ReviewType
    reflection_text: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_suggestions_json: dict = Field(default_factory=dict)


class Review(ReviewBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class Gamification(BaseModel):
    date: date
    streak_days: int
    xp: int
    flow_streak: int


class CoachSuggestionAction(BaseModel):
    title: str
    description: str
    suggestion_type: str


class CoachSuggestion(BaseModel):
    node_type: NodeType
    node_id: int
    actions: list[CoachSuggestionAction]


class CoachRequest(BaseModel):
    node_type: NodeType
    node_id: int
    user_id: int


class ReviewSummary(BaseModel):
    summary: str
    tweaks: list[CoachSuggestionAction]
    completion_rate: float
    flow_score: int


class GraphNode(BaseModel):
    id: int
    type: NodeType
    label: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[Edge]

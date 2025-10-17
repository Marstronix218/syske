from __future__ import annotations

import enum
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class NodeType(str, enum.Enum):
    GOAL = "goal"
    SYSTEM = "system"
    HABIT = "habit"
    TASK = "task"


class RelationType(str, enum.Enum):
    SUPPORTS = "supports"
    TRIGGERS = "triggers"
    FOLLOWS = "follows"


class PlanStatus(str, enum.Enum):
    PLANNED = "planned"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"


class PlanAnchor(str, enum.Enum):
    TIME = "time"
    HABIT = "habit"
    TASK = "task"


class ReviewType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tz: Mapped[str] = mapped_column(String(64), default="America/Argentina/Buenos_Aires")

    goals: Mapped[list["Goal"]] = relationship("Goal", back_populates="user")
    systems: Mapped[list["System"]] = relationship("System", back_populates="user")
    habits: Mapped[list["Habit"]] = relationship("Habit", back_populates="user")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)

    user: Mapped["User"] = relationship("User", back_populates="goals")
    systems: Mapped[list["System"]] = relationship("System", back_populates="goal")


class System(Base):
    __tablename__ = "systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)

    user: Mapped["User"] = relationship("User", back_populates="systems")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="systems")
    habits: Mapped[list["Habit"]] = relationship("Habit", back_populates="system")


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    soft_window_start: Mapped[Optional[time]] = mapped_column(Time, default=None)
    soft_window_end: Mapped[Optional[time]] = mapped_column(Time, default=None)
    energy_tag: Mapped[Optional[str]] = mapped_column(String(32), default=None)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    anchor_event: Mapped[Optional[str]] = mapped_column(String(255), default=None)

    user: Mapped["User"] = relationship("User", back_populates="habits")
    system: Mapped["System"] = relationship("System", back_populates="habits")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="habit")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=3)
    est_minutes: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    energy_tag: Mapped[Optional[str]] = mapped_column(String(32), default=None)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="tasks")
    habit: Mapped[Optional["Habit"]] = relationship("Habit", back_populates="tasks")


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "from_type",
            "from_id",
            "to_type",
            "to_id",
            name="uq_edge_link",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    from_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    from_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    to_id: Mapped[int] = mapped_column(Integer, nullable=False)
    relation: Mapped[RelationType] = mapped_column(Enum(RelationType), nullable=False)


class DayPlan(Base):
    __tablename__ = "day_plans"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    flow_score: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, default=None)

    items: Mapped[list["PlanItem"]] = relationship(
        "PlanItem", back_populates="dayplan", cascade="all, delete-orphan"
    )


class PlanItem(Base):
    __tablename__ = "plan_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dayplan_id: Mapped[int] = mapped_column(ForeignKey("day_plans.id"), index=True, nullable=False)
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    node_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PlanStatus] = mapped_column(Enum(PlanStatus), default=PlanStatus.PLANNED)
    scheduled_order: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    scheduled_window_start: Mapped[Optional[time]] = mapped_column(Time, default=None)
    scheduled_window_end: Mapped[Optional[time]] = mapped_column(Time, default=None)
    anchor: Mapped[Optional[PlanAnchor]] = mapped_column(Enum(PlanAnchor), default=None)

    dayplan: Mapped["DayPlan"] = relationship("DayPlan", back_populates="items")


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    date_range_start: Mapped[date] = mapped_column(Date, nullable=False)
    date_range_end: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[ReviewType] = mapped_column(Enum(ReviewType), nullable=False)
    reflection_text: Mapped[Optional[str]] = mapped_column(Text, default=None)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, default=None)
    ai_suggestions_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Gamification(Base):
    __tablename__ = "gamification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    flow_streak: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_gamification_day"),)


class FailureStats(Base):
    __tablename__ = "failure_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "node_type", "node_id", name="uq_failure_node"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    node_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rolling_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    last_failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)

"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2024-03-06 12:00:00
"""

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tz", sa.String(length=64), nullable=False, server_default="America/Argentina/Buenos_Aires"),
    )

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "systems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("goals.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("system_id", sa.Integer(), sa.ForeignKey("systems.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("soft_window_start", sa.Time(), nullable=True),
        sa.Column("soft_window_end", sa.Time(), nullable=True),
        sa.Column("energy_tag", sa.String(length=32), nullable=True),
        sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
        sa.Column("anchor_event", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("habit_id", sa.Integer(), sa.ForeignKey("habits.id"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("est_minutes", sa.Integer(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("energy_tag", sa.String(length=32), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "edges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_type", sa.Enum("goal", "system", "habit", "task", name="nodetype"), nullable=False),
        sa.Column("from_id", sa.Integer(), nullable=False),
        sa.Column("to_type", sa.Enum("goal", "system", "habit", "task", name="nodetype", create_type=False), nullable=False),
        sa.Column("to_id", sa.Integer(), nullable=False),
        sa.Column(
            "relation",
            sa.Enum("supports", "triggers", "follows", name="relationtype"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "from_type", "from_id", "to_type", "to_id", name="uq_edge_link"),
    )

    op.create_table(
        "day_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("flow_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("user_id", "date", name="uq_user_day"),
    )

    op.create_table(
        "plan_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dayplan_id", sa.Integer(), sa.ForeignKey("day_plans.id"), nullable=False),
        sa.Column("node_type", sa.Enum("goal", "system", "habit", "task", name="nodetype", create_type=False), nullable=False),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("planned", "ready", "in_progress", "done", "skipped", name="planstatus"),
            nullable=False,
            server_default="planned",
        ),
        sa.Column("scheduled_order", sa.Integer(), nullable=True),
        sa.Column("scheduled_window_start", sa.Time(), nullable=True),
        sa.Column("scheduled_window_end", sa.Time(), nullable=True),
        sa.Column(
            "anchor",
            sa.Enum("time", "habit", "task", name="plananchor"),
            nullable=True,
        ),
    )

    op.create_table(
        "event_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date_range_start", sa.Date(), nullable=False),
        sa.Column("date_range_end", sa.Date(), nullable=False),
        sa.Column("type", sa.Enum("daily", "weekly", name="reviewtype"), nullable=False),
        sa.Column("reflection_text", sa.Text(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("ai_suggestions_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    op.create_table(
        "gamification",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("flow_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "date", name="uq_user_gamification_day"),
    )

    op.create_table(
        "failure_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("node_type", sa.Enum("goal", "system", "habit", "task", name="nodetype", create_type=False), nullable=False),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("rolling_fail_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_failed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "node_type", "node_id", name="uq_failure_node"),
    )


def downgrade() -> None:
    op.drop_table("failure_stats")
    op.drop_table("gamification")
    op.drop_table("reviews")
    op.drop_table("event_logs")
    op.drop_table("plan_items")
    op.drop_table("day_plans")
    op.drop_table("edges")
    op.drop_table("tasks")
    op.drop_table("habits")
    op.drop_table("systems")
    op.drop_table("goals")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS nodetype")
    op.execute("DROP TYPE IF EXISTS relationtype")
    op.execute("DROP TYPE IF EXISTS planstatus")
    op.execute("DROP TYPE IF EXISTS plananchor")
    op.execute("DROP TYPE IF EXISTS reviewtype")

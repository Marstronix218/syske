from datetime import date, time

from app.models import Edge, Goal, Habit, NodeType, RelationType, System, Task, User
from app.services import scheduler


def _seed_graph(session):
    user = User(tz="UTC")
    session.add(user)
    session.flush()

    goal = Goal(user_id=user.id, title="Learn", description="")
    session.add(goal)
    session.flush()

    system = System(user_id=user.id, goal_id=goal.id, title="Study System", description="")
    session.add(system)
    session.flush()

    morning = Habit(
        user_id=user.id,
        system_id=system.id,
        name="Morning Review",
        soft_window_start=time(hour=8),
        soft_window_end=time(hour=9),
        recurrence_rule="daily",
    )
    session.add(morning)
    session.flush()

    deep_task = Task(
        user_id=user.id,
        habit_id=morning.id,
        title="Deep Work",
        difficulty=4,
        priority=2,
    )
    session.add(deep_task)
    session.flush()

    session.add(
        Edge(
            user_id=user.id,
            from_type=NodeType.HABIT,
            from_id=morning.id,
            to_type=NodeType.TASK,
            to_id=deep_task.id,
            relation=RelationType.TRIGGERS,
        )
    )
    session.commit()
    return user


def test_scheduler_orders_by_dependency(in_memory_db):
    user = _seed_graph(in_memory_db)
    plan = scheduler.generate_day_plan(in_memory_db, user.id, date.today())
    assert len(plan.items) == 2
    first, second = plan.items
    assert first.node_type == NodeType.HABIT
    assert second.node_type == NodeType.TASK
    assert first.status.name == "READY"

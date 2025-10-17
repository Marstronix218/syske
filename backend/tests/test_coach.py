from datetime import datetime

from app.models import FailureStats, Goal, Habit, NodeType, System, User
from app.services import coach


def test_coach_suggests_actions_when_failures_high(in_memory_db):
    user = User(tz="UTC")
    in_memory_db.add(user)
    in_memory_db.flush()

    goal = Goal(user_id=user.id, title="Goal", description="")
    in_memory_db.add(goal)
    in_memory_db.flush()

    system = System(user_id=user.id, goal_id=goal.id, title="System", description="")
    in_memory_db.add(system)
    in_memory_db.flush()

    habit = Habit(user_id=user.id, system_id=system.id, name="Test Habit")
    in_memory_db.add(habit)
    in_memory_db.flush()

    stats = FailureStats(
        user_id=user.id,
        node_type=NodeType.HABIT,
        node_id=habit.id,
        rolling_fail_count=5,
        last_failed_at=datetime.utcnow(),
    )
    in_memory_db.add(stats)
    in_memory_db.commit()

    suggestion = coach.suggest_fixes(
        in_memory_db, user_id=user.id, node_type=NodeType.HABIT, node_id=habit.id
    )
    assert len(suggestion.actions) >= 3

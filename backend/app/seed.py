from datetime import time

from .database import Base, engine, session_scope
from .models import Edge, Goal, Habit, NodeType, RelationType, System, Task, User


def run() -> None:
    Base.metadata.create_all(bind=engine)

    with session_scope() as session:
        user = session.query(User).first()
        if not user:
            user = User(tz="America/Argentina/Buenos_Aires")
            session.add(user)
            session.flush()

        goal = session.query(Goal).filter(Goal.user_id == user.id, Goal.title == "Thrive Daily").first()
        if not goal:
            goal = Goal(
                user_id=user.id,
                title="Thrive Daily",
                description="Stay energized and move important work forward.",
            )
            session.add(goal)
            session.flush()

        system = (
            session.query(System)
            .filter(System.user_id == user.id, System.title == "Evening Momentum")
            .first()
        )
        if not system:
            system = System(
                user_id=user.id,
                goal_id=goal.id,
                title="Evening Momentum",
                description="Light habits to ease into deep work.",
            )
            session.add(system)
            session.flush()

        habits = {
            "Wake up": (time(hour=8, minute=0), time(hour=9, minute=0), "morning"),
            "Breakfast": (time(hour=10, minute=0), time(hour=10, minute=30), "steady"),
            "Shower": (time(hour=18, minute=0), time(hour=18, minute=30), "evening"),
        }
        created_habits: dict[str, Habit] = {}
        for name, (start, end, energy) in habits.items():
            habit = (
                session.query(Habit)
                .filter(Habit.user_id == user.id, Habit.name == name)
                .first()
            )
            if not habit:
                habit = Habit(
                    user_id=user.id,
                    system_id=system.id,
                    name=name,
                    soft_window_start=start,
                    soft_window_end=end,
                    energy_tag=energy,
                    recurrence_rule="daily",
                )
                session.add(habit)
                session.flush()
            created_habits[name] = habit

        math_task = (
            session.query(Task)
            .filter(Task.user_id == user.id, Task.title == "Math Assignment")
            .first()
        )
        if not math_task:
            math_task = Task(
                user_id=user.id,
                habit_id=created_habits["Shower"].id,
                title="Math Assignment",
                difficulty=3,
                est_minutes=45,
                priority=2,
                energy_tag="evening-focus",
                is_recurring=False,
                active=True,
            )
            session.add(math_task)
            session.flush()

        # Link shower -> math assignment
        existing_edge = (
            session.query(Edge)
            .filter(
                Edge.user_id == user.id,
                Edge.from_type == NodeType.HABIT,
                Edge.from_id == created_habits["Shower"].id,
                Edge.to_type == NodeType.TASK,
                Edge.to_id == math_task.id,
            )
            .first()
        )
        if not existing_edge:
            session.add(
                Edge(
                    user_id=user.id,
                    from_type=NodeType.HABIT,
                    from_id=created_habits["Shower"].id,
                    to_type=NodeType.TASK,
                    to_id=math_task.id,
                    relation=RelationType.TRIGGERS,
                )
            )

        session.commit()


if __name__ == "__main__":
    run()

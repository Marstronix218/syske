import { FormEvent, useState } from "react";

import api from "../api/client";
import { useAppStore } from "../store/appStore";

const LibraryPage = () => {
  const userId = useAppStore((state) => state.userId);
  const habits = useAppStore((state) => state.habits);
  const tasks = useAppStore((state) => state.tasks);
  const fetchLibrary = useAppStore((state) => state.fetchLibrary);
  const fetchGraph = useAppStore((state) => state.fetchGraph);

  const [habitName, setHabitName] = useState("");
  const [habitWindow, setHabitWindow] = useState("18:00");
  const [taskTitle, setTaskTitle] = useState("");
  const [taskHabitId, setTaskHabitId] = useState<number | null>(null);

  const habitList = Object.values(habits);
  const defaultSystemId = habitList[0]?.system_id ?? null;

  const handleHabitSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!userId || !habitName || !defaultSystemId) return;
    await api.post("/habit", {
      user_id: userId,
      system_id: defaultSystemId,
      name: habitName,
      soft_window_start: habitWindow,
      soft_window_end: habitWindow,
      recurrence_rule: "daily",
    });
    setHabitName("");
    await fetchLibrary();
    await fetchGraph();
  };

  const handleTaskSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!userId || !taskTitle) return;
    await api.post("/task", {
      user_id: userId,
      habit_id: taskHabitId,
      title: taskTitle,
      difficulty: 3,
      priority: 1,
      is_recurring: false,
      active: true,
    });
    setTaskTitle("");
    await fetchLibrary();
    await fetchGraph();
  };

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Habit & Task Library</h1>
        <p className="text-sm text-slate-400">
          Build your reusable anchors. Habits trigger tasks instead of strict times.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-lg font-semibold text-slate-100">Habits</h2>
          <form onSubmit={handleHabitSubmit} className="mt-4 space-y-3 text-sm">
            <input
              type="text"
              className="w-full rounded-md border border-slate-700 bg-slate-950/80 p-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Habit name"
              value={habitName}
              onChange={(e) => setHabitName(e.target.value)}
              disabled={!defaultSystemId}
            />
            <input
              type="time"
              className="w-full rounded-md border border-slate-700 bg-slate-950/80 p-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary"
              value={habitWindow}
              onChange={(e) => setHabitWindow(e.target.value)}
              disabled={!defaultSystemId}
            />
            <button
              type="submit"
              className="rounded-md bg-primary px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-700"
              disabled={!defaultSystemId}
            >
              Add habit
            </button>
          </form>
          {!defaultSystemId && (
            <p className="mt-2 text-xs text-amber-300">
              Seed data not loaded yet. Run the backend seed script to enable habit creation.
            </p>
          )}
          <ul className="mt-4 space-y-2 text-sm text-slate-200">
            {habitList.map((habit) => (
              <li key={habit.id} className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
                <p className="font-semibold">{habit.name}</p>
                <p className="text-xs text-slate-500">
                  Window: ~{habit.soft_window_start ?? "open"} | Energy: {habit.energy_tag ?? "flex"}
                </p>
              </li>
            ))}
          </ul>
        </section>
        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-lg font-semibold text-slate-100">Tasks</h2>
          <form onSubmit={handleTaskSubmit} className="mt-4 space-y-3 text-sm">
            <input
              type="text"
              className="w-full rounded-md border border-slate-700 bg-slate-950/80 p-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Task title"
              value={taskTitle}
              onChange={(e) => setTaskTitle(e.target.value)}
            />
            <select
              className="w-full rounded-md border border-slate-700 bg-slate-950/80 p-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary"
              value={taskHabitId ?? ""}
              onChange={(e) =>
                setTaskHabitId(e.target.value ? Number(e.target.value) : null)
              }
            >
              <option value="">No anchor habit</option>
              {habitList.map((habit) => (
                <option key={habit.id} value={habit.id}>
                  After {habit.name}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="rounded-md bg-primary px-4 py-2 font-semibold text-white"
            >
              Add task
            </button>
          </form>
          <ul className="mt-4 space-y-2 text-sm text-slate-200">
            {Object.values(tasks).map((task) => (
              <li key={task.id} className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
                <p className="font-semibold">{task.title}</p>
                <p className="text-xs text-slate-500">
                  Difficulty {task.difficulty} | Follows{" "}
                  {task.habit_id ? habits[task.habit_id]?.name ?? "habit" : "no anchor"}
                </p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
};

export default LibraryPage;

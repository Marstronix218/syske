import { FormEvent, useState } from "react";

import { useAppStore } from "../store/appStore";
import { formatISO } from "../lib/date";

const ReflectionPage = () => {
  const dayPlan = useAppStore((state) => state.dayPlan);
  const fetchDailyReview = useAppStore((state) => state.fetchDailyReview);
  const review = useAppStore((state) => state.lastReview);
  const [energy, setEnergy] = useState(3);
  const [flow, setFlow] = useState(3);
  const [note, setNote] = useState("");

  const planDate = dayPlan?.date ?? formatISO(new Date());

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await fetchDailyReview(planDate);
    // TODO: send answers to backend event log for future AI context.
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Reflection</h1>
        <p className="text-sm text-slate-400">Gentle check-in to spot patterns and tweak the system.</p>
      </div>
      <form
        onSubmit={handleSubmit}
        className="grid gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6"
      >
        <label className="space-y-2 text-sm text-slate-300">
          <span>How aligned was your energy today?</span>
          <input
            className="w-full accent-primary"
            type="range"
            min={1}
            max={5}
            value={energy}
            onChange={(e) => setEnergy(Number(e.target.value))}
          />
          <span className="text-xs text-slate-500">Score: {energy}/5</span>
        </label>
        <label className="space-y-2 text-sm text-slate-300">
          <span>How smooth was your flow sequence?</span>
          <input
            className="w-full accent-primary"
            type="range"
            min={1}
            max={5}
            value={flow}
            onChange={(e) => setFlow(Number(e.target.value))}
          />
          <span className="text-xs text-slate-500">Score: {flow}/5</span>
        </label>
        <label className="space-y-2 text-sm text-slate-300">
          <span>What stood out?</span>
          <textarea
            className="w-full rounded-md border border-slate-700 bg-slate-950/60 p-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary"
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="A tiny win, a snag, or an insight to keep."
          />
        </label>
        <button
          type="submit"
          className="mt-2 self-start rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          Generate AI reflection
        </button>
      </form>

      {review && (
        <div className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">AI Summary</h2>
            <p className="text-sm text-slate-300">{review.summary}</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Suggested tweaks
            </h3>
            <ul className="mt-2 space-y-2 text-sm text-slate-200">
              {review.tweaks.map((action) => (
                <li key={action.suggestion_type} className="rounded-md bg-slate-900 p-3">
                  <p className="font-semibold">{action.title}</p>
                  <p className="text-slate-400">{action.description}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReflectionPage;

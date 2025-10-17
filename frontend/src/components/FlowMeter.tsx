import { Gamification } from "../types";

interface Props {
  gamification: Gamification | null;
  flowScore?: number | null;
}

const FlowMeter = ({ gamification, flowScore }: Props) => {
  if (!gamification) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
        <p className="text-sm text-slate-400">Flow score will appear after your first plan.</p>
      </div>
    );
  }

  const streakLabel =
    gamification.streak_days > 0
      ? `${gamification.streak_days} day streak`
      : "Streak ready to begin";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">Flow Meter</h2>
          <p className="text-sm text-slate-400">Keep the vibe, not the perfect timestamp.</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-primary">{gamification.xp}</p>
          <p className="text-xs uppercase tracking-wide text-slate-500">XP</p>
        </div>
      </div>
      <dl className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
        <div className="rounded-md bg-slate-800/70 p-3">
          <dt className="text-slate-400">Flow streak</dt>
          <dd className="text-xl font-semibold text-energy-high">{gamification.flow_streak}</dd>
        </div>
        <div className="rounded-md bg-slate-800/70 p-3">
          <dt className="text-slate-400">Streak</dt>
          <dd className="text-xl font-semibold text-slate-100">{streakLabel}</dd>
        </div>
        <div className="rounded-md bg-slate-800/70 p-3">
          <dt className="text-slate-400">Daily flow</dt>
          <dd className="text-xl font-semibold text-slate-100">{flowScore ?? 0}</dd>
        </div>
      </dl>
    </div>
  );
};

export default FlowMeter;

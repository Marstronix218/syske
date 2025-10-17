import { PlanItem } from "../types";

interface Props {
  title: string;
  description: string;
  items: PlanItem[];
  getLabel: (item: PlanItem) => string;
  onComplete: (item: PlanItem) => void;
  onSkip: (item: PlanItem) => void;
}

const statusBadge: Record<PlanItem["status"], string> = {
  planned: "bg-slate-800 text-slate-300",
  ready: "bg-emerald-800/40 text-emerald-300",
  in_progress: "bg-primary/20 text-primary",
  done: "bg-emerald-500/30 text-emerald-100",
  skipped: "bg-amber-700/30 text-amber-200",
};

const PlanColumn = ({ title, description, items, getLabel, onComplete, onSkip }: Props) => {
  return (
    <div className="flex-1 rounded-xl border border-slate-800 bg-slate-900/40 px-4 py-5">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
        <p className="text-sm text-slate-400">{description}</p>
      </div>
      <div className="space-y-3">
        {items.length === 0 && <p className="text-sm text-slate-500">Nothing here yet—flow will unlock as you move.</p>}
        {items.map((item) => (
          <div key={item.id} className="rounded-lg border border-slate-800/80 bg-slate-900/80 p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-base font-medium text-slate-100">{getLabel(item)}</p>
                <p className="text-xs uppercase tracking-wide text-slate-500">{item.node_type}</p>
                {item.scheduled_window_start && (
                  <p className="mt-2 text-xs text-slate-400">
                    Window ~{item.scheduled_window_start} → {item.scheduled_window_end ?? "open"}
                  </p>
                )}
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadge[item.status]}`}>
                {item.status.replace("_", " ")}
              </span>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => onComplete(item)}
                className="flex-1 rounded-md bg-primary/80 px-3 py-2 text-sm font-medium text-white transition hover:bg-primary"
              >
                Complete
              </button>
              <button
                onClick={() => onSkip(item)}
                className="flex-1 rounded-md border border-slate-700 px-3 py-2 text-sm font-medium text-slate-200 hover:border-slate-500"
              >
                Skip
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlanColumn;

import { CoachSuggestion } from "../types";

interface Props {
  suggestion: CoachSuggestion | null;
}

const SuggestionPanel = ({ suggestion }: Props) => {
  if (!suggestion) return null;

  return (
    <div className="mt-6 rounded-xl border border-amber-500/40 bg-amber-500/10 p-4">
      <h4 className="text-sm font-semibold uppercase tracking-wide text-amber-300">
        Fail-proof nudge
      </h4>
      <ul className="mt-3 space-y-2">
        {suggestion.actions.map((action) => (
          <li key={action.suggestion_type} className="rounded-md bg-slate-900/70 p-3">
            <p className="text-sm font-semibold text-slate-100">{action.title}</p>
            <p className="text-sm text-slate-300">{action.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SuggestionPanel;

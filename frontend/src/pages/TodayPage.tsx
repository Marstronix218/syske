import { useMemo } from "react";

import FlowMeter from "../components/FlowMeter";
import PlanColumn from "../components/PlanColumn";
import SuggestionPanel from "../components/SuggestionPanel";
import { useAppStore } from "../store/appStore";
import { PlanItem } from "../types";

const TodayPage = () => {
  const dayPlan = useAppStore((state) => state.dayPlan);
  const gamification = useAppStore((state) => state.gamification);
  const habits = useAppStore((state) => state.habits);
  const tasks = useAppStore((state) => state.tasks);
  const completeItem = useAppStore((state) => state.completeItem);
  const skipItem = useAppStore((state) => state.skipItem);
  const requestSuggestion = useAppStore((state) => state.requestSuggestion);
  const suggestion = useAppStore((state) => state.suggestion);

  const getLabel = (item: PlanItem) => {
    if (item.node_type === "habit") {
      return habits[item.node_id]?.name ?? `Habit ${item.node_id}`;
    }
    if (item.node_type === "task") {
      return tasks[item.node_id]?.title ?? `Task ${item.node_id}`;
    }
    return `${item.node_type} ${item.node_id}`;
  };

  const sections = useMemo(() => {
    if (!dayPlan) {
      return {
        now: [] as PlanItem[],
        ready: [] as PlanItem[],
        later: [] as PlanItem[],
      };
    }

    const readyItems = dayPlan.items.filter((item) => item.status === "ready");
    const now = readyItems.slice(0, 1);
    const restReady = readyItems.slice(1);
    const later = dayPlan.items.filter((item) => item.status === "planned");

    return {
      now,
      ready: restReady,
      later,
    };
  }, [dayPlan]);

  const handleComplete = async (item: PlanItem) => {
    await completeItem(item.id);
  };

  const handleSkip = async (item: PlanItem) => {
    await skipItem(item.id, "manual");
    await requestSuggestion(item.node_type, item.node_id);
  };

  return (
    <div className="space-y-6">
      <FlowMeter gamification={gamification} flowScore={dayPlan?.flow_score ?? null} />
      {!dayPlan && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 text-sm text-slate-400">
          Generating your flow map for today…
        </div>
      )}
      {dayPlan && (
        <>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-slate-100">Today&apos;s Flow</h1>
              <p className="text-sm text-slate-400">
                Stay playful. Hit the best next move instead of the perfect clock time.
              </p>
            </div>
            <span className="rounded-full border border-slate-800 px-3 py-1 text-sm text-slate-300">
              {dayPlan.date}
            </span>
          </div>
          <div className="flex gap-4">
            <PlanColumn
              title="Now"
              description="What’s primed and ready. Take the next gentle swing."
              items={sections.now}
              getLabel={getLabel}
              onComplete={handleComplete}
              onSkip={handleSkip}
            />
            <PlanColumn
              title="Ready"
              description="Queued and green-lit once the current move is finished."
              items={sections.ready}
              getLabel={getLabel}
              onComplete={handleComplete}
              onSkip={handleSkip}
            />
            <PlanColumn
              title="Later"
              description="Waiting for anchors or windows. No pressure."
              items={sections.later}
              getLabel={getLabel}
              onComplete={handleComplete}
              onSkip={handleSkip}
            />
          </div>
          <SuggestionPanel suggestion={suggestion} />
        </>
      )}
    </div>
  );
};

export default TodayPage;

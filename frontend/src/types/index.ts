export type NodeType = "goal" | "system" | "habit" | "task";
export type PlanStatus = "planned" | "ready" | "in_progress" | "done" | "skipped";
export type PlanAnchor = "time" | "habit" | "task" | null;

export interface PlanItem {
  id: number;
  node_type: NodeType;
  node_id: number;
  status: PlanStatus;
  scheduled_order: number | null;
  scheduled_window_start: string | null;
  scheduled_window_end: string | null;
  anchor: PlanAnchor;
}

export interface DayPlan {
  id: number;
  user_id: number;
  date: string;
  generated_at: string;
  flow_score: number;
  notes: string | null;
  items: PlanItem[];
}

export interface Gamification {
  date: string;
  streak_days: number;
  xp: number;
  flow_streak: number;
}

export interface CoachAction {
  title: string;
  description: string;
  suggestion_type: string;
}

export interface CoachSuggestion {
  node_type: NodeType;
  node_id: number;
  actions: CoachAction[];
}

export interface ReviewSummary {
  summary: string;
  tweaks: CoachAction[];
  completion_rate: number;
  flow_score: number;
}

export interface GraphNode {
  id: number;
  type: NodeType;
  label: string;
}

export interface GraphEdge {
  id: number;
  user_id: number;
  from_type: NodeType;
  from_id: number;
  to_type: NodeType;
  to_id: number;
  relation: "supports" | "triggers" | "follows";
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Habit {
  id: number;
  user_id: number;
  system_id: number;
  name: string;
  soft_window_start: string | null;
  soft_window_end: string | null;
  energy_tag: string | null;
  recurrence_rule: string | null;
  anchor_event: string | null;
}

export interface Task {
  id: number;
  user_id: number;
  habit_id: number | null;
  title: string;
  difficulty: number;
  est_minutes: number | null;
  priority: number;
  energy_tag: string | null;
  is_recurring: boolean;
  active: boolean;
}

import { create } from "zustand";

import api from "../api/client";
import {
  CoachSuggestion,
  DayPlan,
  Gamification,
  GraphResponse,
  ReviewSummary,
} from "../types";

interface AppState {
  userId: number | null;
  dayPlan: DayPlan | null;
  gamification: Gamification | null;
  graph: GraphResponse | null;
  lastReview: ReviewSummary | null;
  suggestion: CoachSuggestion | null;
  habits: Record<number, import("../types").Habit>;
  tasks: Record<number, import("../types").Task>;
  isLoadingPlan: boolean;
  init: () => Promise<void>;
  fetchPlan: (planDate: string) => Promise<void>;
  completeItem: (planItemId: number) => Promise<void>;
  skipItem: (planItemId: number, reason?: string) => Promise<void>;
  fetchGamification: (planDate: string) => Promise<void>;
  fetchGraph: () => Promise<void>;
  fetchLibrary: () => Promise<void>;
  fetchDailyReview: (planDate: string) => Promise<ReviewSummary | null>;
  requestSuggestion: (nodeType: string, nodeId: number) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  userId: null,
  dayPlan: null,
  gamification: null,
  graph: null,
  lastReview: null,
  suggestion: null,
  habits: {},
  tasks: {},
  isLoadingPlan: false,

  init: async () => {
    const { data } = await api.post("/auth/devlogin");
    set({ userId: data.id });
  },

  fetchPlan: async (planDate: string) => {
    const userId = get().userId;
    if (!userId) return;
    set({ isLoadingPlan: true });
    try {
      try {
        const { data } = await api.get("/plan", {
          params: {
            user_id: userId,
            plan_date: planDate,
          },
        });
        set({ dayPlan: data });
      } catch (error: any) {
        if (error.response?.status === 404) {
          const { data } = await api.post("/plan/generate", null, {
            params: {
              user_id: userId,
              plan_date: planDate,
            },
          });
          set({ dayPlan: data.plan });
        } else {
          throw error;
        }
      }
    } finally {
      set({ isLoadingPlan: false });
    }
  },

  completeItem: async (planItemId: number) => {
    const { userId, dayPlan } = get();
    if (!userId || !dayPlan) return;
    await api.post(
      "/plan/complete",
      { plan_item_id: planItemId },
      { params: { user_id: userId } },
    );
    await get().fetchPlan(dayPlan.date);
    await get().fetchGamification(dayPlan.date);
  },

  skipItem: async (planItemId: number, reason?: string) => {
    const { userId, dayPlan } = get();
    if (!userId || !dayPlan) return;
    await api.post(
      "/plan/skip",
      { plan_item_id: planItemId, reason },
      { params: { user_id: userId } },
    );
    await get().fetchPlan(dayPlan.date);
    await get().fetchGamification(dayPlan.date);
  },

  fetchGamification: async (planDate: string) => {
    const userId = get().userId;
    if (!userId) return;
    const { data } = await api.get("/gamification/today", {
      params: { user_id: userId, target_date: planDate },
    });
    set({ gamification: data });
  },

  fetchGraph: async () => {
    const userId = get().userId;
    if (!userId) return;
    const { data } = await api.get("/graph", { params: { user_id: userId } });
    set({ graph: data });
  },

  fetchLibrary: async () => {
    const userId = get().userId;
    if (!userId) return;
    const [habitsRes, tasksRes] = await Promise.all([
      api.get("/habit/" + userId),
      api.get("/task/" + userId),
    ]);
    const habitsMap = Object.fromEntries(
      habitsRes.data.map((habit: { id: number }) => [habit.id, habit]),
    );
    const tasksMap = Object.fromEntries(
      tasksRes.data.map((task: { id: number }) => [task.id, task]),
    );
    set({ habits: habitsMap, tasks: tasksMap });
  },

  fetchDailyReview: async (planDate: string) => {
    const userId = get().userId;
    if (!userId) return null;
    const { data } = await api.get("/review/daily", {
      params: { user_id: userId, target_date: planDate },
    });
    set({ lastReview: data });
    return data;
  },

  requestSuggestion: async (nodeType: string, nodeId: number) => {
    const userId = get().userId;
    if (!userId) return;
    const { data } = await api.post("/coach/suggest", {
      user_id: userId,
      node_type: nodeType,
      node_id: nodeId,
    });
    set({ suggestion: data });
  },
}));

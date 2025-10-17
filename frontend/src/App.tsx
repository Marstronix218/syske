import { useEffect } from "react";
import { NavLink, Route, Routes } from "react-router-dom";

import TodayPage from "./pages/TodayPage";
import SystemMapPage from "./pages/SystemMapPage";
import ReflectionPage from "./pages/ReflectionPage";
import LibraryPage from "./pages/LibraryPage";
import { useAppStore } from "./store/appStore";
import { formatISO } from "./lib/date";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium ${
    isActive ? "bg-primary text-white" : "text-slate-200 hover:bg-slate-800"
  }`;

function App() {
  const init = useAppStore((state) => state.init);
  const userId = useAppStore((state) => state.userId);
  const fetchPlan = useAppStore((state) => state.fetchPlan);
  const fetchGamification = useAppStore((state) => state.fetchGamification);
  const fetchGraph = useAppStore((state) => state.fetchGraph);
  const fetchLibrary = useAppStore((state) => state.fetchLibrary);

  useEffect(() => {
    init();
  }, [init]);

  useEffect(() => {
    if (!userId) return;
    const today = formatISO(new Date());
    fetchPlan(today);
    fetchGamification(today);
    fetchGraph();
    fetchLibrary();
  }, [userId, fetchPlan, fetchGamification, fetchGraph, fetchLibrary]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold text-primary">Syske Flow</span>
          <nav className="flex gap-2">
            <NavLink to="/" className={navLinkClass} end>
              Today
            </NavLink>
            <NavLink to="/map" className={navLinkClass}>
              System Map
            </NavLink>
            <NavLink to="/reflection" className={navLinkClass}>
              Reflection
            </NavLink>
            <NavLink to="/library" className={navLinkClass}>
              Library
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-6">
        <Routes>
          <Route path="/" element={<TodayPage />} />
          <Route path="/map" element={<SystemMapPage />} />
          <Route path="/reflection" element={<ReflectionPage />} />
          <Route path="/library" element={<LibraryPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

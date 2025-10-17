import { useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";

import { useAppStore } from "../store/appStore";

const nodeColors = {
  goal: "#38bdf8",
  system: "#a855f7",
  habit: "#22c55e",
  task: "#fbbf24",
};

const SystemMapPage = () => {
  const graph = useAppStore((state) => state.graph);

  const data = useMemo(() => {
    if (!graph) {
      return { nodes: [], links: [] };
    }
    return {
      nodes: graph.nodes.map((node) => ({
        id: `${node.type}-${node.id}`,
        name: node.label,
        type: node.type,
      })),
      links: graph.edges.map((edge) => ({
        source: `${edge.from_type}-${edge.from_id}`,
        target: `${edge.to_type}-${edge.to_id}`,
        relation: edge.relation,
      })),
    };
  }, [graph]);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">System Map</h1>
        <p className="text-sm text-slate-400">
          Explore how goals, systems, habits, and tasks interact. Drag to reorganize, zoom to inspect.
        </p>
      </div>
      <div className="h-[520px] rounded-xl border border-slate-800 bg-slate-900/60 p-2">
        {data.nodes.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            No nodes yet—add habits or tasks to see the map bloom.
          </div>
        ) : (
          <ForceGraph2D
            graphData={data}
            nodeAutoColorBy="type"
            backgroundColor="rgba(2,6,23,1)"
            linkColor={() => "rgba(148,163,184,0.6)"}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.name;
              const fontSize = 12 / globalScale;
              ctx.fillStyle = nodeColors[(node as any).type as keyof typeof nodeColors] ?? "#94a3b8";
              ctx.beginPath();
              ctx.arc(node.x ?? 0, node.y ?? 0, 6, 0, 2 * Math.PI);
              ctx.fill();

              ctx.font = `${fontSize}px Inter`;
              ctx.fillStyle = "#e2e8f0";
              ctx.fillText(label, (node.x ?? 0) + 8, node.y ?? 0 + 4);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default SystemMapPage;

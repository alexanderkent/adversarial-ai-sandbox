import type { Metric } from "../api";

export function MetricBars({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="flex flex-col gap-2">
      {metrics.map((m) => (
        <div key={m.label} className="text-sm">
          <div className="flex justify-between">
            <span className="text-slate-600">{m.label}</span>
            <span className="font-medium tabular-nums">{m.display}</span>
          </div>
          <div className="h-2 rounded bg-slate-200">
            <div
              className="h-2 rounded bg-indigo-500"
              style={{ width: `${Math.max(0, Math.min(1, m.value)) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

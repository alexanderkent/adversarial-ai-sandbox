import type { Metric } from "../api";

export function MetricBars({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="flex flex-col gap-3">
      {metrics.map((m) => (
        <div key={m.label} className="text-sm">
          <div className="mb-1 flex items-baseline justify-between">
            <span className="text-ink-muted">{m.label}</span>
            <span className="text-base font-semibold tabular-nums text-ink">{m.display}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-surface-2">
            <div
              className="h-2 rounded-full transition-[width] duration-500"
              style={{ width: `${Math.max(0, Math.min(1, m.value)) * 100}%`, background: "var(--primary)" }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

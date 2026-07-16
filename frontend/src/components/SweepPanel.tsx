import { useEffect, useRef, useState } from "react";
import { streamSweep, type Params, type SweepPoint, type SweepSpec } from "../api";
import { SweepChart } from "./SweepChart";

export interface SweepPanelProps {
  attackId: string;
  spec: SweepSpec;
  params: Params;
}

export function SweepPanel({ attackId, spec, params }: SweepPanelProps) {
  const [points, setPoints] = useState<SweepPoint[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);
  // reset when the target attack changes
  useEffect(() => { setPoints([]); setError(null); }, [attackId]);

  const total = spec.x_values.length;
  const done = points.filter((p) => typeof p.x === "number").length;

  async function runSweep() {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setPoints([]);
    setError(null);
    setRunning(true);
    try {
      for await (const p of streamSweep(attackId, params, ac.signal)) {
        if (p.done) break;
        setPoints((prev) => [...prev, p]);
      }
    } catch (e) {
      if (!ac.signal.aborted) setError(e instanceof Error ? e.message : "Sweep failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <button
          onClick={runSweep}
          disabled={running}
          className="rounded bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {running ? "Sweeping…" : "Run sweep"}
        </button>
        <span className="text-sm text-slate-500 tabular-nums">{done} / {total}</span>
      </div>
      <div className="flex gap-4 text-xs text-slate-600">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-3 rounded-sm" style={{ background: "#6366f1" }} />
          {spec.attacked_metric} (attacked)
        </span>
        {spec.defended_metric && (
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-3 rounded-sm" style={{ background: "#10b981" }} />
            {spec.defended_metric} (defended)
          </span>
        )}
      </div>
      <SweepChart
        points={points}
        xLabel={spec.x_label}
        yLabel={spec.y_label}
        attackedLabel={spec.attacked_metric}
        defendedLabel={spec.defended_metric}
      />
      {error && <div className="rounded bg-red-50 p-2 text-sm text-red-700" role="alert">{error}</div>}
      <p className="text-xs text-slate-400">Sweeps <code>{spec.x_knob}</code> across {total} values; other knobs use their current values.</p>
    </div>
  );
}

import type { RunResult } from "../api";
import { MetricBars } from "./MetricBars";
import { TranscriptView } from "./TranscriptView";

interface Props {
  result: RunResult | null;
  loading: boolean;
  error: string | null;
}

export function ArtifactPanel({ result, loading, error }: Props) {
  if (loading) {
    return <div className="p-8 text-center text-slate-500">Running…</div>;
  }
  if (error) {
    return (
      <div className="rounded bg-red-50 p-4 text-red-700" role="alert">
        {error}
      </div>
    );
  }
  if (!result) {
    return <div className="p-8 text-center text-slate-400">Adjust the knobs and press Run.</div>;
  }
  return (
    <div className="flex flex-col gap-4">
      {result.transcript ? (
        <TranscriptView transcript={result.transcript} />
      ) : result.figure ? (
        <figure className="m-0">
          <img
            src={`data:image/png;base64,${result.figure.png_base64}`}
            alt={result.figure.caption || "attack artifact"}
            className="w-full rounded border border-slate-200"
          />
          {result.figure.caption && (
            <figcaption className="mt-1 text-xs text-slate-500">{result.figure.caption}</figcaption>
          )}
        </figure>
      ) : null}
      <MetricBars metrics={result.metrics} />
      <p className="text-sm text-slate-700">{result.narrative}</p>
    </div>
  );
}

import type { RunResult } from "../api";
import { MetricBars } from "./MetricBars";
import { TranscriptView } from "./TranscriptView";
import { TextComparisonView } from "./TextComparisonView";

interface Props {
  result: RunResult | null;
  loading: boolean;
  error: string | null;
}

export function ArtifactPanel({ result, loading, error }: Props) {
  if (loading) {
    return <div className="p-8 text-center text-ink-muted">Running…</div>;
  }
  if (error) {
    return (
      <div className="rounded-lg bg-danger/10 p-4 text-danger" role="alert">
        {error}
      </div>
    );
  }
  if (!result) {
    return <div className="p-8 text-center text-ink-subtle">Adjust the knobs and press Run.</div>;
  }
  return (
    <div className="rounded-xl border border-border bg-surface p-4 shadow-[var(--shadow)]">
      <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-subtle">Results</div>
      <div className="flex flex-col gap-4">
        {result.transcript ? (
          <TranscriptView transcript={result.transcript} />
        ) : result.text_comparison ? (
          <TextComparisonView comparison={result.text_comparison} />
        ) : result.figure ? (
          <figure className="m-0">
            <img
              src={`data:image/png;base64,${result.figure.png_base64}`}
              alt={result.figure.caption || "attack artifact"}
              className="w-full rounded-lg border border-border"
            />
            {result.figure.caption && (
              <figcaption className="mt-1 text-xs text-ink-subtle">{result.figure.caption}</figcaption>
            )}
          </figure>
        ) : null}
        <MetricBars metrics={result.metrics} />
        <p className="text-sm text-ink-muted">{result.narrative}</p>
      </div>
    </div>
  );
}

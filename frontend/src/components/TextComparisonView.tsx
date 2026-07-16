import type { TextComparison } from "../api";

export function TextComparisonView({ comparison }: { comparison: TextComparison }) {
  return (
    <div className="flex flex-col gap-3">
      {comparison.variants.map((v, i) => (
        <div key={i} className="rounded-lg border border-border p-2">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-ink-subtle">
              {v.label}
            </span>
            <span className="text-xs font-medium tabular-nums text-ink-muted">
              injection: <span>{v.score_display}</span>
            </span>
          </div>
          <p className="whitespace-pre-wrap break-words font-mono text-sm text-ink">
            {v.spans.map((s, j) =>
              s.changed ? (
                <span key={j} data-testid="span-changed" className="rounded" style={{ background: "var(--highlight)" }}>
                  {s.text}
                </span>
              ) : (
                <span key={j}>{s.text}</span>
              ),
            )}
          </p>
        </div>
      ))}
      {comparison.caption && (
        <p className="text-xs text-ink-subtle">{comparison.caption}</p>
      )}
    </div>
  );
}

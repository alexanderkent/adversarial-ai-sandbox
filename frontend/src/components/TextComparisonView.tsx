import type { TextComparison } from "../api";

export function TextComparisonView({ comparison }: { comparison: TextComparison }) {
  return (
    <div className="flex flex-col gap-3">
      {comparison.variants.map((v, i) => (
        <div key={i} className="rounded border border-slate-200 p-2">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              {v.label}
            </span>
            <span className="text-xs font-medium tabular-nums text-slate-600">
              injection: <span>{v.score_display}</span>
            </span>
          </div>
          <p className="whitespace-pre-wrap break-words font-mono text-sm text-slate-800">
            {v.spans.map((s, j) =>
              s.changed ? (
                <span key={j} data-testid="span-changed" className="rounded bg-amber-200 text-amber-900">
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
        <p className="text-xs text-slate-500">{comparison.caption}</p>
      )}
    </div>
  );
}

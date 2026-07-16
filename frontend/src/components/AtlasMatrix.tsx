import type { AtlasMatrix as AtlasMatrixData } from "../api";

interface Props {
  matrix: AtlasMatrixData;
  onSelectAttack: (attackId: string) => void;
  focusId?: string | null;
}

export function AtlasMatrix({ matrix, onSelectAttack, focusId }: Props) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4 shadow-[var(--shadow)]">
      <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-subtle">
        MITRE ATLAS — coverage matrix
      </div>
      <div className="flex gap-3 overflow-x-auto">
        {matrix.tactics.map((col) => (
          <div key={col.tactic} className="min-w-[160px] flex-1">
            <div className="mb-2 border-b-2 border-primary-soft pb-2 text-[10px] font-semibold uppercase tracking-wide text-ink-subtle">
              {col.tactic}
            </div>
            <div className="flex flex-col gap-2">
              {col.cells.map((cell) => (
                <div
                  key={cell.id}
                  data-testid="atlas-cell"
                  data-covered={cell.covered ? "true" : "false"}
                  className={
                    cell.covered
                      ? `rounded-lg bg-primary p-2 text-xs text-on-primary ${
                          focusId === cell.id ? "ring-2 ring-primary-strong" : ""
                        }`
                      : "rounded-lg border border-dashed border-border bg-surface-2 p-2 text-xs text-ink-subtle"
                  }
                >
                  <div className="flex items-start justify-between gap-1">
                    <div>
                      <div className="font-semibold">{cell.id}</div>
                      <div>{cell.name}</div>
                    </div>
                    <a
                      href={cell.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`${cell.id} on MITRE ATLAS`}
                      className="opacity-70 transition hover:opacity-100"
                    >
                      ↗
                    </a>
                  </div>
                  {cell.covered && cell.attacks.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {cell.attacks.map((a) => (
                        <button
                          key={a.attack_id}
                          type="button"
                          onClick={() => onSelectAttack(a.attack_id)}
                          className="rounded-full bg-white/20 px-2 py-0.5 text-[10px] transition hover:bg-white/30"
                        >
                          {a.attack_name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

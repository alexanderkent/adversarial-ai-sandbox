import { useState } from "react";
import type { FlowStep, FlowActor } from "../api";

const ACTOR: Record<FlowActor, string> = {
  input: "var(--ink-subtle)",
  attacker: "var(--primary)",
  model: "var(--warn)",
  defense: "var(--accent)",
  outcome: "var(--danger)",
};
const ACTOR_ORDER: FlowActor[] = ["input", "attacker", "model", "defense", "outcome"];

export function FlowPanel({ steps }: { steps: FlowStep[] }) {
  const [active, setActive] = useState(0);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-3 text-xs text-ink-muted">
        {ACTOR_ORDER.map((a) => (
          <span key={a} className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2 w-2 rounded-full" style={{ background: ACTOR[a] }} />
            {a}
          </span>
        ))}
      </div>

      <div className="flex items-stretch gap-1 overflow-x-auto pb-1">
        {steps.map((s, i) => (
          <div key={i} className="flex items-stretch">
            {i > 0 && <div className="flex items-center px-1 text-ink-subtle">→</div>}
            <button
              type="button"
              data-testid="flow-step"
              data-actor={s.actor}
              data-active={i === active}
              onClick={() => setActive(i)}
              className={`min-w-[130px] max-w-[180px] flex-1 rounded-lg border p-2 text-left transition ${
                i === active ? "border-primary bg-primary-soft" : "border-border bg-surface hover:bg-surface-2"
              }`}
            >
              <div className="mb-1.5 h-1 w-8 rounded-full" style={{ background: ACTOR[s.actor] }} />
              <div className="text-xs font-semibold text-ink">{s.title}</div>
              <div className="mt-0.5 text-[11px] leading-snug text-ink-muted">{s.detail}</div>
            </button>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          aria-label="Previous step"
          disabled={active === 0}
          onClick={() => setActive((a) => Math.max(0, a - 1))}
          className="rounded-md border border-border px-2 py-1 text-sm text-ink-muted transition hover:text-ink disabled:opacity-40"
        >
          ❮
        </button>
        <button
          type="button"
          aria-label="Next step"
          disabled={active === steps.length - 1}
          onClick={() => setActive((a) => Math.min(steps.length - 1, a + 1))}
          className="rounded-md border border-border px-2 py-1 text-sm text-ink-muted transition hover:text-ink disabled:opacity-40"
        >
          ❯
        </button>
        <span className="text-xs tabular-nums text-ink-subtle">
          Step {active + 1} of {steps.length}
        </span>
      </div>
    </div>
  );
}

import type { Knob } from "../api";

interface Props {
  knob: Knob;
  value: number | boolean | string;
  onChange: (value: number | boolean | string) => void;
}

export function KnobControl({ knob, value, onChange }: Props) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-ink">{knob.label}</span>

      {knob.type === "slider" && (
        <div className="flex items-center gap-2">
          <input
            type="range"
            aria-label={knob.label}
            min={knob.min ?? 0}
            max={knob.max ?? 100}
            step={knob.step ?? 1}
            value={Number(value)}
            onChange={(e) => onChange(Number(e.target.value))}
            className="flex-1 accent-[var(--primary)]"
          />
          <span className="w-10 text-right tabular-nums text-ink-muted">{Number(value)}</span>
        </div>
      )}

      {knob.type === "toggle" && (
        <input
          type="checkbox"
          aria-label={knob.label}
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
          className="h-4 w-4 accent-[var(--primary)]"
        />
      )}

      {knob.type === "select" && (
        <select
          aria-label={knob.label}
          value={String(value)}
          onChange={(e) => onChange(e.target.value)}
          className="rounded-lg border border-border bg-surface px-2 py-1 text-ink"
        >
          {(knob.options ?? []).map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      )}

      {knob.help && <span className="text-xs text-ink-subtle">{knob.help}</span>}
    </label>
  );
}

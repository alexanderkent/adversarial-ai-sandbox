import type { AttackDescription, Params } from "../api";
import { KnobControl } from "./KnobControl";

interface Props {
  description: AttackDescription;
  params: Params;
  onParamChange: (name: string, value: number | boolean | string) => void;
  defenseOn: boolean;
  onDefenseToggle: (on: boolean) => void;
  onRun: () => void;
  loading: boolean;
}

export function ControlPanel({
  description,
  params,
  onParamChange,
  defenseOn,
  onDefenseToggle,
  onRun,
  loading,
}: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-3">
        {description.knobs.map((knob) => (
          <KnobControl
            key={knob.name}
            knob={knob}
            value={params[knob.name]}
            onChange={(v) => onParamChange(knob.name, v)}
          />
        ))}
      </div>

      {description.has_defense && (
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={defenseOn}
            onChange={(e) => onDefenseToggle(e.target.checked)}
          />
          <span>Apply defense</span>
        </label>
      )}

      <button
        onClick={onRun}
        disabled={loading}
        className="rounded bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? "Running…" : defenseOn ? "Run with defense" : "Run attack"}
      </button>
    </div>
  );
}

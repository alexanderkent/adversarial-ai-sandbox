import { useEffect, useState } from "react";
import { API_BASE, getAttack, type AttackDescription, type Params } from "../api";
import { useRun } from "../hooks/useRun";
import { LessonPanel } from "./LessonPanel";
import { ControlPanel } from "./ControlPanel";
import { ArtifactPanel } from "./ArtifactPanel";

export function AttackView({ attackId }: { attackId: string }) {
  const [description, setDescription] = useState<AttackDescription | null>(null);
  const [params, setParams] = useState<Params>({});
  const [defenseOn, setDefenseOn] = useState(false);
  const [descError, setDescError] = useState<string | null>(null);
  const { result, loading, error, execute, reset } = useRun(attackId);

  useEffect(() => {
    let active = true;
    setDescription(null);
    reset();
    setDefenseOn(false);
    setDescError(null);
    getAttack(attackId)
      .then((d) => {
        if (!active) return;
        setDescription(d);
        const seeded: Params = {};
        d.knobs.forEach((k) => {
          seeded[k.name] = k.default;
        });
        setParams(seeded);
      })
      .catch((e) => {
        if (!active) return;
        setDescError(e instanceof Error ? e.message : "Failed to load attack");
      });
    return () => {
      active = false;
    };
  }, [attackId, reset]);

  if (descError) {
    return <div className="rounded bg-red-50 p-4 text-red-700" role="alert">{descError} — is the backend running at {API_BASE}?</div>;
  }
  if (!description) {
    return <div className="p-8 text-slate-400">Loading…</div>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
      <div className="flex flex-col gap-6">
        <LessonPanel description={description} />
        <ControlPanel
          description={description}
          params={params}
          onParamChange={(name, value) => setParams((p) => ({ ...p, [name]: value }))}
          defenseOn={defenseOn}
          onDefenseToggle={setDefenseOn}
          onRun={() => execute(defenseOn ? "defend" : "run", params)}
          loading={loading}
        />
      </div>
      <ArtifactPanel result={result} loading={loading} error={error} />
    </div>
  );
}

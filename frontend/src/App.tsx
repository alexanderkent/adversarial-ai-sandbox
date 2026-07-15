import { useEffect, useState } from "react";
import { listAttacks, type AttackSummary } from "./api";
import { AttackSidebar } from "./components/AttackSidebar";
import { AttackView } from "./components/AttackView";

export default function App() {
  const [attacks, setAttacks] = useState<AttackSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAttacks()
      .then((list) => {
        setAttacks(list);
        setSelectedId((cur) => cur ?? list[0]?.id ?? null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load attacks"));
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold">Adversarial Sandbox</h1>
        <p className="text-sm text-slate-500">Tinker with adversarial ML attacks and defenses</p>
      </header>
      <div className="grid gap-6 p-6 md:grid-cols-[220px_1fr]">
        <aside>
          {error ? (
            <div className="rounded bg-red-50 p-3 text-sm text-red-700" role="alert">
              {error} — is the backend running on :8000?
            </div>
          ) : (
            <AttackSidebar attacks={attacks} selectedId={selectedId} onSelect={setSelectedId} />
          )}
        </aside>
        <main>{selectedId && <AttackView attackId={selectedId} />}</main>
      </div>
    </div>
  );
}

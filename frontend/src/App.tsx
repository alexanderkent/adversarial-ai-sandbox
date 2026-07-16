import { useEffect, useState } from "react";
import { API_BASE, listAttacks, listAtlas, type AttackSummary, type AtlasMatrix as AtlasMatrixData } from "./api";
import { AttackSidebar } from "./components/AttackSidebar";
import { AttackView } from "./components/AttackView";
import { AtlasMatrix } from "./components/AtlasMatrix";
import { ThemeToggle } from "./components/ThemeToggle";

export default function App() {
  const [attacks, setAttacks] = useState<AttackSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"attack" | "atlas">("attack");
  const [atlas, setAtlas] = useState<AtlasMatrixData | null>(null);
  const [atlasFocus, setAtlasFocus] = useState<string | null>(null);

  useEffect(() => {
    listAttacks()
      .then((list) => {
        setAttacks(list);
        setSelectedId((cur) => cur ?? list[0]?.id ?? null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load attacks"));
    listAtlas().then(setAtlas).catch(() => {});
  }, []);

  function showAttack(id: string) {
    setSelectedId(id);
    setView("attack");
  }
  function showTechnique(techniqueId: string) {
    setAtlasFocus(techniqueId);
    setView("atlas");
  }

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <header className="flex items-center justify-between border-b border-border bg-surface px-6 py-4">
        <div>
          <h1 className="text-xl font-bold">Adversarial Sandbox</h1>
          <p className="text-sm text-ink-muted">Tinker with adversarial ML attacks and defenses</p>
        </div>
        <ThemeToggle />
      </header>
      <div className="grid gap-6 p-6 md:grid-cols-[220px_1fr]">
        <aside>
          {error ? (
            <div className="rounded-lg bg-danger/10 p-3 text-sm text-danger" role="alert">
              {error} — is the backend running at {API_BASE}?
            </div>
          ) : (
            <AttackSidebar
              attacks={attacks}
              selectedId={view === "attack" ? selectedId : null}
              onSelect={showAttack}
              atlasActive={view === "atlas"}
              onShowAtlas={() => {
                setAtlasFocus(null);
                setView("atlas");
              }}
            />
          )}
        </aside>
        <main>
          {view === "atlas"
            ? atlas && <AtlasMatrix matrix={atlas} onSelectAttack={showAttack} focusId={atlasFocus} />
            : selectedId && <AttackView key={selectedId} attackId={selectedId} onShowTechnique={showTechnique} />}
        </main>
      </div>
    </div>
  );
}

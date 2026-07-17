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
    <div className="flex min-h-screen flex-col bg-canvas text-ink">
      <header className="flex items-center justify-between border-b border-border bg-surface px-6 py-4">
        <div>
          <h1 className="text-xl font-bold">Adversarial AI Sandbox</h1>
          <p className="text-sm text-ink-muted">Tinker with adversarial ML attacks and defenses</p>
        </div>
        <ThemeToggle />
      </header>
      <div className="grid flex-1 gap-6 p-6 md:grid-cols-[220px_1fr]">
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
      <footer className="mt-auto border-t border-border bg-surface text-sm text-ink-muted">
        <div
          className="h-1 w-full"
          style={{ background: "linear-gradient(90deg, var(--primary), var(--accent), var(--danger))" }}
        />
        <div className="flex flex-col gap-3 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-semibold text-ink">Adversarial AI Sandbox</p>
            <p>Every attack ships with its defense — because attacks are only half the story.</p>
          </div>
          <div className="flex flex-col gap-1 md:items-end">
            <p>
              Built with <span className="text-ink">React</span> ·{" "}
              <span className="text-ink">FastAPI</span> · <span className="text-ink">PyTorch</span>
            </p>
            <p className="flex items-center gap-2">
              <a
                className="text-primary hover:underline"
                href="https://github.com/alexanderkent/adversarial-ai-sandbox"
                target="_blank"
                rel="noreferrer"
              >
                GitHub
              </a>
              <span aria-hidden>·</span>
              <span>MIT License</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

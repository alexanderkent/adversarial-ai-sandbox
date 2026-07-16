import type { AttackSummary } from "../api";

interface Props {
  attacks: AttackSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function AttackSidebar({ attacks, selectedId, onSelect }: Props) {
  const groups: string[] = [];
  for (const a of attacks) {
    if (!groups.includes(a.group)) groups.push(a.group);
  }

  return (
    <nav className="flex flex-col gap-4">
      {groups.map((group) => (
        <div key={group}>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink-subtle">{group}</h3>
          <ul className="flex flex-col gap-1">
            {attacks
              .filter((a) => a.group === group)
              .map((a) => (
                <li key={a.id}>
                  <button
                    onClick={() => onSelect(a.id)}
                    aria-current={a.id === selectedId}
                    className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${a.id === selectedId ? "bg-primary-soft font-medium text-primary" : "text-ink-muted hover:bg-surface-2 hover:text-ink"}`}
                  >
                    {a.name}
                  </button>
                </li>
              ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

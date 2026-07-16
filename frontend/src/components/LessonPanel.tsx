import ReactMarkdown from "react-markdown";
import type { AttackDescription } from "../api";
import { Formula } from "./Formula";

export function LessonPanel({
  description,
  onShowTechnique,
}: {
  description: AttackDescription;
  onShowTechnique?: (techniqueId: string) => void;
}) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-ink">{description.name}</h2>
      {description.atlas && description.atlas.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {description.atlas.map((t) => (
            <span
              key={t.id}
              className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-2.5 py-0.5 text-xs font-semibold text-primary"
            >
              <button onClick={() => onShowTechnique?.(t.id)} className="hover:underline">
                {t.id} · {t.name}
              </button>
              <a
                href={t.url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`${t.id} on MITRE ATLAS`}
                className="opacity-60 transition hover:opacity-100"
              >
                ↗
              </a>
            </span>
          ))}
        </div>
      )}
      <div className="text-sm leading-relaxed text-ink-muted [&_strong]:font-semibold [&_strong]:text-ink">
        <ReactMarkdown>{description.summary}</ReactMarkdown>
      </div>
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-subtle">Formula</h3>
        <Formula tex={description.formula} />
      </div>
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-subtle">Threat model</h3>
        <p className="mt-1 text-sm text-ink-muted">{description.threat_model}</p>
      </div>
    </div>
  );
}

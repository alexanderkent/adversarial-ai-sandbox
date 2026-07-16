import ReactMarkdown from "react-markdown";
import type { AttackDescription } from "../api";
import { Formula } from "./Formula";

export function LessonPanel({ description }: { description: AttackDescription }) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-ink">{description.name}</h2>
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

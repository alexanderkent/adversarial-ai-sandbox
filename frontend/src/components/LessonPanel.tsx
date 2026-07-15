import ReactMarkdown from "react-markdown";
import type { AttackDescription } from "../api";

export function LessonPanel({ description }: { description: AttackDescription }) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-slate-800">{description.name}</h2>
      <div className="text-sm leading-relaxed text-slate-700 [&_strong]:font-semibold">
        <ReactMarkdown>{description.summary}</ReactMarkdown>
      </div>
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Formula</h3>
        <pre className="mt-1 overflow-x-auto rounded bg-slate-100 p-2 text-xs">{description.formula}</pre>
      </div>
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Threat model</h3>
        <p className="mt-1 text-sm text-slate-600">{description.threat_model}</p>
      </div>
    </div>
  );
}

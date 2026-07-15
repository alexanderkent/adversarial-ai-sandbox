import type { CodeSnippet } from "../api";
import { CodeBlock } from "./CodeBlock";

export function CodePanel({ code }: { code: CodeSnippet[] }) {
  if (!code.length) {
    return <p className="p-4 text-sm text-slate-400">No code available for this attack.</p>;
  }
  return (
    <div className="flex flex-col gap-4">
      {code.map((s) => (
        <div key={s.label}>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{s.label}</h3>
          <CodeBlock source={s.source} language={s.language} />
        </div>
      ))}
    </div>
  );
}

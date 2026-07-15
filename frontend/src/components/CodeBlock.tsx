import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import "highlight.js/styles/github.css";

hljs.registerLanguage("python", python);

export function CodeBlock({ source, language = "python" }: { source: string; language?: string }) {
  const lang = hljs.getLanguage(language) ? language : "python";
  const html = hljs.highlight(source, { language: lang }).value;
  return (
    <pre className="overflow-x-auto rounded border border-slate-200 bg-slate-50 p-3 text-xs leading-relaxed">
      <code className="hljs language-python" dangerouslySetInnerHTML={{ __html: html }} />
    </pre>
  );
}

import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import "highlight.js/styles/github-dark.css";

hljs.registerLanguage("python", python);

export function CodeBlock({ source, language = "python" }: { source: string; language?: string }) {
  const lang = hljs.getLanguage(language) ? language : "python";
  const html = hljs.highlight(source, { language: lang }).value;
  return (
    <pre className="overflow-x-auto rounded-lg border border-border bg-[#0d1117] p-3 text-xs leading-relaxed">
      <code className="hljs language-python" dangerouslySetInnerHTML={{ __html: html }} />
    </pre>
  );
}

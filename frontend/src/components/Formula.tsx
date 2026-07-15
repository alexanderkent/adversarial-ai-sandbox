import katex from "katex";
import "katex/dist/katex.min.css";

export function Formula({ tex }: { tex: string }) {
  const html = katex.renderToString(tex, { throwOnError: false, displayMode: true });
  return (
    <div className="overflow-x-auto py-1 text-slate-800" dangerouslySetInnerHTML={{ __html: html }} />
  );
}

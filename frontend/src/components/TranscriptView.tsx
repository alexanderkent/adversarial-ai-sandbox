import type { Transcript, TranscriptTurn } from "../api";

const ROLE_LABEL: Record<TranscriptTurn["role"], string> = {
  system: "System prompt",
  document: "Retrieved document (untrusted)",
  user: "User",
  assistant: "Assistant",
};

const ROLE_STYLE: Record<TranscriptTurn["role"], string> = {
  system: "bg-slate-100 text-slate-700",
  document: "bg-amber-50 text-amber-900 border border-amber-200",
  user: "bg-indigo-50 text-indigo-900",
  assistant: "bg-white text-slate-800 border border-slate-200",
};

export function TranscriptView({ transcript }: { transcript: Transcript }) {
  return (
    <div className="flex flex-col gap-2">
      {transcript.turns.map((turn, i) => (
        <div
          key={i}
          data-testid="transcript-turn"
          data-injected={turn.injected ? "true" : "false"}
          className={`rounded p-2 text-sm ${ROLE_STYLE[turn.role]} ${
            turn.injected ? "ring-2 ring-red-400" : ""
          }`}
        >
          <div className="mb-0.5 text-[10px] font-semibold uppercase tracking-wide opacity-60">
            {ROLE_LABEL[turn.role]}
            {turn.injected && <span className="ml-1 text-red-600">• injected</span>}
          </div>
          <div className="whitespace-pre-wrap">{turn.content}</div>
        </div>
      ))}
      {transcript.caption && (
        <p className="mt-1 text-xs text-slate-500">{transcript.caption}</p>
      )}
    </div>
  );
}

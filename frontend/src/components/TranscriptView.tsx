import type { Transcript, TranscriptTurn } from "../api";

const ROLE_LABEL: Record<TranscriptTurn["role"], string> = {
  system: "System prompt",
  document: "Retrieved document (untrusted)",
  user: "User",
  assistant: "Assistant",
};

const ROLE_STYLE: Record<TranscriptTurn["role"], string> = {
  system: "bg-surface-2 text-ink-muted",
  document: "bg-warn/10 text-ink border border-warn/40",
  user: "bg-primary-soft text-ink",
  assistant: "bg-surface text-ink border border-border",
};

export function TranscriptView({ transcript }: { transcript: Transcript }) {
  return (
    <div className="flex flex-col gap-2">
      {transcript.turns.map((turn, i) => (
        <div
          key={i}
          data-testid="transcript-turn"
          data-injected={turn.injected ? "true" : "false"}
          className={`rounded-lg p-2 text-sm ${ROLE_STYLE[turn.role]} ${
            turn.injected ? "ring-2 ring-danger" : ""
          }`}
        >
          <div className="mb-0.5 text-[10px] font-semibold uppercase tracking-wide opacity-70">
            {ROLE_LABEL[turn.role]}
            {turn.injected && <span className="ml-1 text-danger">• injected</span>}
          </div>
          <div className="whitespace-pre-wrap">{turn.content}</div>
        </div>
      ))}
      {transcript.caption && (
        <p className="mt-1 text-xs text-ink-subtle">{transcript.caption}</p>
      )}
    </div>
  );
}

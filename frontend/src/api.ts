export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export type KnobType = "slider" | "toggle" | "select";

export interface Knob {
  name: string;
  label: string;
  type: KnobType;
  default: number | boolean | string;
  min?: number | null;
  max?: number | null;
  step?: number | null;
  options?: string[] | null;
  help?: string;
}

export interface AttackSummary {
  id: string;
  name: string;
  group: string;
  summary: string;
}

export interface SweepSpec {
  x_knob: string;
  x_values: number[];
  x_label: string;
  y_label: string;
  attacked_metric: string;
  defended_metric: string | null;
}

export interface SweepPoint {
  x?: number;
  attacked?: number;
  defended?: number;
  error?: string;
  done?: boolean;
}

export interface AttackDescription extends AttackSummary {
  formula: string;
  threat_model: string;
  flow?: FlowStep[];
  knobs: Knob[];
  has_defense: boolean;
  code?: CodeSnippet[];
  sweep?: SweepSpec | null;
  atlas?: AtlasTechnique[];
}

export interface CodeSnippet {
  label: string;
  language: string;
  source: string;
}

export interface AtlasSubtechnique {
  id: string;
  name: string;
}

export interface AtlasTechnique {
  id: string;
  name: string;
  tactic: string;
  url: string;
  subtechniques?: AtlasSubtechnique[];
}

export type FlowActor = "input" | "attacker" | "model" | "defense" | "outcome";

export interface FlowStep {
  title: string;
  detail: string;
  actor: FlowActor;
}

export interface AtlasAttackRef {
  attack_id: string;
  attack_name: string;
}

export interface AtlasCell {
  id: string;
  name: string;
  url: string;
  covered: boolean;
  subtechniques?: AtlasSubtechnique[];
  attacks: AtlasAttackRef[];
}

export interface AtlasColumn {
  tactic: string;
  cells: AtlasCell[];
}

export interface AtlasMatrix {
  tactics: AtlasColumn[];
}

export interface Figure {
  kind: "figure";
  png_base64: string;
  caption: string;
}

export interface Metric {
  label: string;
  value: number;
  display: string;
}

export interface TranscriptTurn {
  role: "system" | "user" | "document" | "assistant";
  content: string;
  injected?: boolean;
}

export interface Transcript {
  kind: "transcript";
  turns: TranscriptTurn[];
  caption?: string;
}

export interface TextSpan {
  text: string;
  changed?: boolean;
}

export interface TextVariant {
  label: string;
  spans: TextSpan[];
  score: number;
  score_display: string;
}

export interface TextComparison {
  kind: "text_comparison";
  variants: TextVariant[];
  caption?: string;
}

export interface DecisionDomain {
  x_min: number;
  x_max: number;
  y_min: number;
  y_max: number;
}

export interface DecisionPoint {
  x: number;
  y: number;
  label: number;
  poison?: boolean;
}

export interface DecisionState {
  title: string;
  domain: DecisionDomain;
  grid: number[][];
  resolution: number;
  points: DecisionPoint[];
  accuracy: number;
}

export interface DecisionSurface {
  kind: "decision_surface";
  states: DecisionState[];
  caption?: string;
}

export interface RunResult {
  figure?: Figure | null;
  metrics: Metric[];
  narrative: string;
  transcript?: Transcript | null;
  text_comparison?: TextComparison | null;
  decision_surface?: DecisionSurface | null;
}

export type Params = Record<string, number | boolean | string>;

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function toJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText || `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body && typeof body.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

function post(path: string, params: Params): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function listAttacks(): Promise<AttackSummary[]> {
  return toJson(await fetch(`${API_BASE}/attacks`));
}

export async function getAttack(id: string): Promise<AttackDescription> {
  return toJson(await fetch(`${API_BASE}/attacks/${id}`));
}

export async function listAtlas(): Promise<AtlasMatrix> {
  return toJson(await fetch(`${API_BASE}/atlas`));
}

export async function runAttack(id: string, params: Params): Promise<RunResult> {
  return toJson(await post(`/attacks/${id}/run`, params));
}

export async function defendAttack(id: string, params: Params): Promise<RunResult> {
  return toJson(await post(`/attacks/${id}/defend`, params));
}

export async function* streamSweep(
  id: string,
  params: Params,
  signal?: AbortSignal,
): AsyncGenerator<SweepPoint> {
  const res = await fetch(`${API_BASE}/attacks/${id}/sweep`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(params),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new ApiError(res.status, res.statusText || `HTTP ${res.status}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let nl: number;
    while ((nl = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, nl).trim();
      buffer = buffer.slice(nl + 1);
      if (line) yield JSON.parse(line) as SweepPoint;
    }
  }
  const tail = buffer.trim();
  if (tail) yield JSON.parse(tail) as SweepPoint;
}

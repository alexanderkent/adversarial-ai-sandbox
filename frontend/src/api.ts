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

export interface AttackDescription extends AttackSummary {
  formula: string;
  threat_model: string;
  knobs: Knob[];
  has_defense: boolean;
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

export interface RunResult {
  figure: Figure;
  metrics: Metric[];
  narrative: string;
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

export async function runAttack(id: string, params: Params): Promise<RunResult> {
  return toJson(await post(`/attacks/${id}/run`, params));
}

export async function defendAttack(id: string, params: Params): Promise<RunResult> {
  return toJson(await post(`/attacks/${id}/defend`, params));
}

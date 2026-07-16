import { afterEach, expect, test, vi } from "vitest";
import { listAttacks, runAttack, streamSweep, type SweepPoint } from "./api";

afterEach(() => vi.unstubAllGlobals());

function mockFetch(status: number, body: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: status >= 200 && status < 300,
      status,
      statusText: "",
      json: async () => body,
    })),
  );
}

test("listAttacks returns parsed array", async () => {
  mockFetch(200, [{ id: "poisoning", name: "Data Poisoning", group: "Poisoning", summary: "s" }]);
  const attacks = await listAttacks();
  expect(attacks[0].id).toBe("poisoning");
});

test("runAttack posts params and returns result", async () => {
  const spy = vi.fn(
    (_url: RequestInfo | URL, _init?: RequestInit): Promise<Response> =>
      Promise.resolve({
        ok: true, status: 200, statusText: "",
        json: async () => ({ figure: { kind: "figure", png_base64: "abc", caption: "" }, metrics: [], narrative: "n" }),
      } as unknown as Response),
  );
  vi.stubGlobal("fetch", spy);
  const res = await runAttack("poisoning", { flip_pct: 20 });
  expect(res.figure.png_base64).toBe("abc");
  const [url, init] = spy.mock.calls[0];
  expect(String(url)).toContain("/attacks/poisoning/run");
  expect(JSON.parse(init!.body as string)).toEqual({ flip_pct: 20 });
});

test("non-2xx throws ApiError with detail", async () => {
  mockFetch(422, { detail: "flip_pct=999 above max 50" });
  await expect(runAttack("poisoning", { flip_pct: 999 })).rejects.toMatchObject({
    name: "ApiError",
    status: 422,
    message: "flip_pct=999 above max 50",
  });
});

function streamResponse(chunks: string[]): Response {
  const enc = new TextEncoder();
  const body = new ReadableStream({
    start(c) {
      for (const ch of chunks) c.enqueue(enc.encode(ch));
      c.close();
    },
  });
  return new Response(body, { status: 200, headers: { "content-type": "application/x-ndjson" } });
}

test("streamSweep parses NDJSON across chunk boundaries", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    // note: second point is split across the two chunks
    streamResponse(['{"x":0,"attacked":0.1}\n{"x":1,"atta', 'cked":0.2}\n{"done":true}\n']),
  );
  const got: SweepPoint[] = [];
  for await (const p of streamSweep("poisoning", {})) got.push(p);
  expect(got).toEqual([
    { x: 0, attacked: 0.1 },
    { x: 1, attacked: 0.2 },
    { done: true },
  ]);
});

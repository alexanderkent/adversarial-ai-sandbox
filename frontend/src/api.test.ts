import { afterEach, expect, test, vi } from "vitest";
import { listAttacks, runAttack } from "./api";

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

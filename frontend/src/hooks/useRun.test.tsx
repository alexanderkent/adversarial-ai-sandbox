import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import * as api from "../api";
import { useRun } from "./useRun";

afterEach(() => vi.restoreAllMocks());

const result = { figure: { kind: "figure" as const, png_base64: "x", caption: "" }, metrics: [], narrative: "n" };

test("execute('run') calls runAttack and stores result", async () => {
  const runSpy = vi.spyOn(api, "runAttack").mockResolvedValue(result);
  const { result: hook } = renderHook(() => useRun("poisoning"));
  await act(async () => { await hook.current.execute("run", { flip_pct: 20 }); });
  expect(runSpy).toHaveBeenCalledWith("poisoning", { flip_pct: 20 });
  expect(hook.current.result?.narrative).toBe("n");
  expect(hook.current.loading).toBe(false);
});

test("execute('defend') calls defendAttack", async () => {
  const defSpy = vi.spyOn(api, "defendAttack").mockResolvedValue(result);
  const { result: hook } = renderHook(() => useRun("poisoning"));
  await act(async () => { await hook.current.execute("defend", {}); });
  expect(defSpy).toHaveBeenCalled();
});

test("errors are captured as a string message", async () => {
  vi.spyOn(api, "runAttack").mockRejectedValue(new api.ApiError(503, "checkpoint missing"));
  const { result: hook } = renderHook(() => useRun("perturbation"));
  await act(async () => { await hook.current.execute("run", {}); });
  await waitFor(() => expect(hook.current.error).toBe("checkpoint missing"));
});

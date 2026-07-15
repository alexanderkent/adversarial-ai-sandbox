import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import * as api from "../api";
import { AttackView } from "./AttackView";

afterEach(() => vi.restoreAllMocks());

const desc: api.AttackDescription = {
  id: "poisoning", name: "Data Poisoning", group: "Poisoning", summary: "s",
  formula: "f", threat_model: "t", has_defense: true,
  knobs: [{ name: "flip_pct", label: "Flip %", type: "slider", min: 0, max: 50, step: 1, default: 20 }],
};
const result: api.RunResult = {
  figure: { kind: "figure", png_base64: "AAAA", caption: "" },
  metrics: [], narrative: "done",
};

test("loads description then runs the attack with seeded params", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(desc);
  const runSpy = vi.spyOn(api, "runAttack").mockResolvedValue(result);
  render(<AttackView attackId="poisoning" />);

  await waitFor(() => expect(screen.getByRole("heading", { name: "Data Poisoning" })).toBeInTheDocument());
  fireEvent.click(screen.getByRole("button", { name: /run attack/i }));
  await waitFor(() => expect(runSpy).toHaveBeenCalledWith("poisoning", { flip_pct: 20 }));
});

test("defense toggle routes Run to defendAttack", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(desc);
  const defSpy = vi.spyOn(api, "defendAttack").mockResolvedValue(result);
  render(<AttackView attackId="poisoning" />);

  await waitFor(() => screen.getByRole("heading", { name: "Data Poisoning" }));
  fireEvent.click(screen.getByLabelText(/apply defense/i));
  fireEvent.click(screen.getByRole("button", { name: /run with defense/i }));
  await waitFor(() => expect(defSpy).toHaveBeenCalledWith("poisoning", { flip_pct: 20 }));
});

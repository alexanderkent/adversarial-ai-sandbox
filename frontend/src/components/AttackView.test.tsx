import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import * as api from "../api";
import { AttackView } from "./AttackView";

afterEach(() => vi.restoreAllMocks());

const desc: api.AttackDescription = {
  id: "poisoning", name: "Data Poisoning", group: "Poisoning", summary: "s",
  formula: "f", threat_model: "t", has_defense: true,
  knobs: [{ name: "flip_pct", label: "Flip %", type: "slider", min: 0, max: 50, step: 1, default: 20 }],
  code: [{ label: "FGSM", language: "python", source: "def fgsm():\n    pass" }],
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

test("shows an error when the description fetch fails", async () => {
  vi.spyOn(api, "getAttack").mockRejectedValue(new api.ApiError(404, "Unknown attack"));
  render(<AttackView attackId="nope" />);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Unknown attack"));
});

test("switches to the Code tab and shows the source", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(desc);
  render(<AttackView attackId="poisoning" />);
  await waitFor(() => screen.getByRole("heading", { name: "Data Poisoning" }));
  fireEvent.click(screen.getByRole("tab", { name: "Code" }));
  expect(screen.getByText("FGSM")).toBeInTheDocument();
});

const descWithSweep: api.AttackDescription = {
  ...desc,
  id: "perturbation",
  name: "Perturbation",
  sweep: {
    x_knob: "epsilon",
    x_values: [0, 0.1],
    x_label: "Epsilon",
    y_label: "Confidence",
    attacked_metric: "Adversarial confidence",
    defended_metric: "Adversarial confidence",
  },
};

test("shows a Sweep tab and panel when the description has a sweep spec", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(descWithSweep);
  render(<AttackView attackId="perturbation" />);
  await waitFor(() => screen.getByRole("heading", { name: "Perturbation" }));
  const sweepTab = screen.getByRole("tab", { name: /sweep/i });
  fireEvent.click(sweepTab);
  expect(screen.getByRole("button", { name: /run sweep/i })).toBeInTheDocument();
});

test("hides the Sweep tab when the description has no sweep spec", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(desc);
  render(<AttackView attackId="poisoning" />);
  await waitFor(() => screen.getByRole("heading", { name: "Data Poisoning" }));
  expect(screen.queryByRole("tab", { name: /sweep/i })).not.toBeInTheDocument();
});

const descWithFlow: api.AttackDescription = {
  ...desc,
  flow: [
    { title: "Clean input", detail: "x", actor: "input" },
    { title: "Model misclassifies", detail: "wrong", actor: "outcome" },
  ],
};

test("shows a Flow tab and pipeline when the description has a flow", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(descWithFlow);
  render(<AttackView attackId="poisoning" />);
  await waitFor(() => screen.getByRole("heading", { name: "Data Poisoning" }));
  fireEvent.click(screen.getByRole("tab", { name: "Flow" }));
  expect(screen.getAllByTestId("flow-step")).toHaveLength(2);
});

test("hides the Flow tab when the description has no flow", async () => {
  vi.spyOn(api, "getAttack").mockResolvedValue(desc);
  render(<AttackView attackId="poisoning" />);
  await waitFor(() => screen.getByRole("heading", { name: "Data Poisoning" }));
  expect(screen.queryByRole("tab", { name: "Flow" })).not.toBeInTheDocument();
});

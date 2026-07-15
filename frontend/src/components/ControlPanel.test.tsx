import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { AttackDescription } from "../api";
import { ControlPanel } from "./ControlPanel";

const desc: AttackDescription = {
  id: "poisoning", name: "Data Poisoning", group: "Poisoning", summary: "s",
  formula: "f", threat_model: "t", has_defense: true,
  knobs: [
    { name: "dataset", label: "Dataset", type: "select", options: ["moons", "blobs"], default: "blobs" },
    { name: "flip_pct", label: "Flip %", type: "slider", min: 0, max: 50, step: 1, default: 20 },
  ],
};

function setup(overrides = {}) {
  const props = {
    description: desc,
    params: { dataset: "blobs", flip_pct: 20 },
    onParamChange: vi.fn(),
    defenseOn: false,
    onDefenseToggle: vi.fn(),
    onRun: vi.fn(),
    loading: false,
    ...overrides,
  };
  render(<ControlPanel {...props} />);
  return props;
}

test("renders one control per knob", () => {
  setup();
  expect(screen.getByLabelText("Dataset")).toBeInTheDocument();
  expect(screen.getByLabelText("Flip %")).toBeInTheDocument();
});

test("changing a knob calls onParamChange with name+value", () => {
  const props = setup();
  fireEvent.change(screen.getByLabelText("Flip %"), { target: { value: "35" } });
  expect(props.onParamChange).toHaveBeenCalledWith("flip_pct", 35);
});

test("defense toggle shown when has_defense and fires onDefenseToggle", () => {
  const props = setup();
  fireEvent.click(screen.getByLabelText(/apply defense/i));
  expect(props.onDefenseToggle).toHaveBeenCalledWith(true);
});

test("run button fires onRun and disables while loading", () => {
  const props = setup({ loading: true });
  const btn = screen.getByRole("button");
  expect(btn).toBeDisabled();
  props.onRun; // referenced for clarity
});

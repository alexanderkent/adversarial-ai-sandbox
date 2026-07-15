import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { Knob } from "../api";
import { KnobControl } from "./KnobControl";

test("slider emits a number", () => {
  const knob: Knob = { name: "flip_pct", label: "Flip %", type: "slider", min: 0, max: 50, step: 1, default: 20 };
  const onChange = vi.fn();
  render(<KnobControl knob={knob} value={20} onChange={onChange} />);
  const slider = screen.getByLabelText("Flip %");
  fireEvent.change(slider, { target: { value: "30" } });
  expect(onChange).toHaveBeenCalledWith(30);
});

test("select renders options and emits a string", () => {
  const knob: Knob = { name: "dataset", label: "Dataset", type: "select", options: ["moons", "blobs"], default: "blobs" };
  const onChange = vi.fn();
  render(<KnobControl knob={knob} value="blobs" onChange={onChange} />);
  expect(screen.getByRole("option", { name: "moons" })).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Dataset"), { target: { value: "moons" } });
  expect(onChange).toHaveBeenCalledWith("moons");
});

test("toggle emits a boolean", () => {
  const knob: Knob = { name: "on", label: "Defense", type: "toggle", default: false };
  const onChange = vi.fn();
  render(<KnobControl knob={knob} value={false} onChange={onChange} />);
  fireEvent.click(screen.getByLabelText("Defense"));
  expect(onChange).toHaveBeenCalledWith(true);
});

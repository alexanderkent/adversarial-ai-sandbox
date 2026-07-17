import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import type { DecisionSurface } from "../api";
import { DecisionSurfaceView } from "./DecisionSurfaceView";

const dom = { x_min: -3, x_max: 3, y_min: -3, y_max: 3 };
const surface: DecisionSurface = {
  kind: "decision_surface",
  states: [
    { title: "Clean model", domain: dom, resolution: 2, grid: [[0, 1], [0, 1]],
      points: [{ x: -2, y: -2, label: 0, poison: false }], accuracy: 0.9 },
    { title: "Poisoned model", domain: dom, resolution: 2, grid: [[0, 0], [1, 1]],
      points: [{ x: -2, y: -2, label: 0, poison: false },
               { x: 0, y: 0, label: 1, poison: true }], accuracy: 0.6 },
  ],
  caption: "toggle me",
};

test("renders active state points, accuracy, and toggles between states", async () => {
  render(<DecisionSurfaceView surface={surface} />);
  expect(screen.getByRole("button", { name: "Clean model" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getAllByTestId("decision-point")).toHaveLength(1);
  expect(screen.getByText(/90%/)).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Poisoned model" }));
  expect(screen.getByRole("button", { name: "Poisoned model" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getAllByTestId("decision-point")).toHaveLength(2);
  expect(screen.getByText(/60%/)).toBeInTheDocument();
});

test("marks poison points and shows a tooltip on hover", async () => {
  render(<DecisionSurfaceView surface={surface} />);
  await userEvent.click(screen.getByRole("button", { name: "Poisoned model" }));
  const poison = screen.getAllByTestId("decision-point").find(
    (el) => el.getAttribute("data-poison") === "true");
  expect(poison).toBeTruthy();
  fireEvent.mouseEnter(poison!);
  expect(screen.getByTestId("decision-tooltip")).toBeInTheDocument();
});

import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import type { AttackDescription } from "../api";
import { LessonPanel } from "./LessonPanel";

const desc: AttackDescription = {
  id: "poisoning", name: "Data Poisoning", group: "Poisoning",
  summary: "Data poisoning corrupts the **training set**.",
  formula: "y_i -> 1 - y_i", threat_model: "Attacker modifies labels.",
  has_defense: true, knobs: [],
};

test("renders name, summary text, formula and threat model", () => {
  render(<LessonPanel description={desc} />);
  expect(screen.getByRole("heading", { name: "Data Poisoning" })).toBeInTheDocument();
  expect(screen.getByText(/Data poisoning corrupts the/)).toBeInTheDocument();
  expect(screen.getByText("y_i -> 1 - y_i")).toBeInTheDocument();
  expect(screen.getByText("Attacker modifies labels.")).toBeInTheDocument();
});

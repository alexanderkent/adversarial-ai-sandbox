import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import type { AttackDescription } from "../api";
import { LessonPanel } from "./LessonPanel";

const desc: AttackDescription = {
  id: "poisoning", name: "Data Poisoning", group: "Poisoning",
  summary: "Data poisoning corrupts the **training set**.",
  formula: "x_{adv} = x + \\epsilon", threat_model: "Attacker modifies labels.",
  has_defense: true, knobs: [],
};

test("renders name, summary text, formula and threat model", () => {
  const { container } = render(<LessonPanel description={desc} />);
  expect(screen.getByRole("heading", { name: "Data Poisoning" })).toBeInTheDocument();
  expect(screen.getByText(/Data poisoning corrupts the/)).toBeInTheDocument();
  expect(container.querySelector(".katex")).toBeTruthy();
  expect(screen.getByText("Attacker modifies labels.")).toBeInTheDocument();
});

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";
import type { AttackDescription } from "../api";
import { LessonPanel } from "./LessonPanel";

const desc: AttackDescription = {
  id: "poisoning", name: "Data Poisoning", group: "Poisoning",
  summary: "Data poisoning corrupts the **training set**.",
  formula: "x_{adv} = x + \\epsilon", threat_model: "Attacker modifies labels.",
  has_defense: true, knobs: [],
  atlas: [{ id: "AML.T0020", name: "Poison Training Data", tactic: "Resource Development",
            url: "https://atlas.mitre.org/techniques/AML.T0020" }],
};

test("renders name, summary text, formula and threat model", () => {
  const { container } = render(<LessonPanel description={desc} />);
  expect(screen.getByRole("heading", { name: "Data Poisoning" })).toBeInTheDocument();
  expect(screen.getByText(/Data poisoning corrupts the/)).toBeInTheDocument();
  expect(container.querySelector(".katex")).toBeTruthy();
  expect(screen.getByText("Attacker modifies labels.")).toBeInTheDocument();
});

test("renders an ATLAS badge that links out and fires onShowTechnique", async () => {
  const onShow = vi.fn();
  render(<LessonPanel description={desc} onShowTechnique={onShow} />);
  expect(screen.getByText(/AML\.T0020 · Poison Training Data/)).toBeInTheDocument();
  const link = screen.getByRole("link", { name: /AML\.T0020 on MITRE ATLAS/i });
  expect(link).toHaveAttribute("href", "https://atlas.mitre.org/techniques/AML.T0020");
  await userEvent.click(screen.getByRole("button", { name: /AML\.T0020 · Poison Training Data/ }));
  expect(onShow).toHaveBeenCalledWith("AML.T0020");
});

test("renders no badge row when atlas is empty", () => {
  render(<LessonPanel description={{ ...desc, atlas: [] }} />);
  expect(screen.queryByText(/AML\.T/)).not.toBeInTheDocument();
});

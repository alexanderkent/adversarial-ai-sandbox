import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";
import type { AtlasMatrix as AtlasMatrixData } from "../api";
import { AtlasMatrix } from "./AtlasMatrix";

const matrix: AtlasMatrixData = {
  tactics: [
    { tactic: "Defense Evasion", cells: [
      { id: "AML.T0015", name: "Evade ML Model", url: "u1", covered: true,
        attacks: [{ attack_id: "perturbation", attack_name: "Adversarial Perturbation" }] },
    ] },
    { tactic: "Impact", cells: [
      { id: "AML.T0031", name: "Erode ML Model Integrity", url: "u2", covered: false, attacks: [] },
    ] },
  ],
};

test("renders covered and context cells distinctly", () => {
  render(<AtlasMatrix matrix={matrix} onSelectAttack={() => {}} />);
  const cells = screen.getAllByTestId("atlas-cell");
  expect(cells).toHaveLength(2);
  expect(cells.find((c) => c.textContent?.includes("AML.T0015"))).toHaveAttribute("data-covered", "true");
  expect(cells.find((c) => c.textContent?.includes("AML.T0031"))).toHaveAttribute("data-covered", "false");
});

test("clicking a covered cell's attack tag fires onSelectAttack", async () => {
  const onSelect = vi.fn();
  render(<AtlasMatrix matrix={matrix} onSelectAttack={onSelect} />);
  await userEvent.click(screen.getByRole("button", { name: "Adversarial Perturbation" }));
  expect(onSelect).toHaveBeenCalledWith("perturbation");
});

test("context cell renders no attack button", () => {
  render(<AtlasMatrix matrix={matrix} onSelectAttack={() => {}} />);
  expect(screen.queryByRole("button", { name: /Erode/ })).not.toBeInTheDocument();
});

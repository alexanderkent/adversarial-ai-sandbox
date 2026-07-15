import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { AttackSummary } from "../api";
import { AttackSidebar } from "./AttackSidebar";

const attacks: AttackSummary[] = [
  { id: "poisoning", name: "Data Poisoning", group: "Poisoning", summary: "" },
  { id: "perturbation", name: "Adversarial Perturbation", group: "Perturbation", summary: "" },
];

test("renders group headings and attack buttons", () => {
  render(<AttackSidebar attacks={attacks} selectedId="poisoning" onSelect={() => {}} />);
  expect(screen.getByText("Poisoning")).toBeInTheDocument();
  expect(screen.getByText("Perturbation")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Data Poisoning" })).toHaveAttribute("aria-current", "true");
});

test("clicking an attack calls onSelect", () => {
  const onSelect = vi.fn();
  render(<AttackSidebar attacks={attacks} selectedId="poisoning" onSelect={onSelect} />);
  fireEvent.click(screen.getByRole("button", { name: "Adversarial Perturbation" }));
  expect(onSelect).toHaveBeenCalledWith("perturbation");
});

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import type { FlowStep } from "../api";
import { FlowPanel } from "./FlowPanel";

const steps: FlowStep[] = [
  { title: "Clean input", detail: "x", actor: "input" },
  { title: "Perturb", detail: "x + eps", actor: "attacker" },
  { title: "Misclassified", detail: "wrong", actor: "outcome" },
];

test("renders a card per step with its actor and a legend", () => {
  render(<FlowPanel steps={steps} />);
  const cards = screen.getAllByTestId("flow-step");
  expect(cards).toHaveLength(3);
  expect(cards[0]).toHaveAttribute("data-actor", "input");
  expect(cards[1]).toHaveAttribute("data-actor", "attacker");
  // legend lists the actor names
  expect(screen.getByText("outcome")).toBeInTheDocument();
});

test("first step active by default; ❯ advances and ❮ goes back, clamped", async () => {
  render(<FlowPanel steps={steps} />);
  const cards = () => screen.getAllByTestId("flow-step");
  expect(cards()[0]).toHaveAttribute("data-active", "true");

  await userEvent.click(screen.getByRole("button", { name: /next step/i }));
  expect(cards()[1]).toHaveAttribute("data-active", "true");
  expect(cards()[0]).toHaveAttribute("data-active", "false");

  await userEvent.click(screen.getByRole("button", { name: /previous step/i }));
  await userEvent.click(screen.getByRole("button", { name: /previous step/i })); // clamp at 0
  expect(cards()[0]).toHaveAttribute("data-active", "true");
});

test("clicking a step activates it", async () => {
  render(<FlowPanel steps={steps} />);
  await userEvent.click(screen.getAllByTestId("flow-step")[2]);
  expect(screen.getAllByTestId("flow-step")[2]).toHaveAttribute("data-active", "true");
});

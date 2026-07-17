import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";
import * as api from "./api";
import App from "./App";

afterEach(() => vi.restoreAllMocks());

const attacks: api.AttackSummary[] = [
  { id: "poisoning", name: "Data Poisoning", group: "Poisoning", summary: "s" },
];
const desc: api.AttackDescription = {
  ...attacks[0], formula: "f", threat_model: "t", has_defense: true,
  knobs: [{ name: "flip_pct", label: "Flip %", type: "slider", min: 0, max: 50, step: 1, default: 20 }],
};

test("loads attacks and shows the first attack's view", async () => {
  vi.spyOn(api, "listAttacks").mockResolvedValue(attacks);
  vi.spyOn(api, "getAttack").mockResolvedValue(desc);
  render(<App />);
  expect(screen.getByRole("heading", { name: /adversarial ai sandbox/i })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByRole("button", { name: "Data Poisoning" })).toBeInTheDocument());
  await waitFor(() => expect(screen.getByRole("heading", { name: "Data Poisoning" })).toBeInTheDocument());
});

test("shows an error hint when the list fails", async () => {
  vi.spyOn(api, "listAttacks").mockRejectedValue(new api.ApiError(0, "Failed to fetch"));
  render(<App />);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/backend/i));
});

test("MITRE ATLAS entry switches to the matrix and back", async () => {
  vi.spyOn(api, "listAttacks").mockResolvedValue(attacks);
  vi.spyOn(api, "getAttack").mockResolvedValue({ ...desc, atlas: [] });
  vi.spyOn(api, "listAtlas").mockResolvedValue({
    tactics: [{ tactic: "Defense Evasion", cells: [
      { id: "AML.T0015", name: "Evade ML Model", url: "u", covered: true,
        attacks: [{ attack_id: "poisoning", attack_name: "Data Poisoning" }] }] }],
  });
  render(<App />);
  await userEvent.click(await screen.findByRole("button", { name: /MITRE ATLAS/i }));
  expect(await screen.findByText(/coverage matrix/i)).toBeInTheDocument();
  const cell = screen.getByTestId("atlas-cell");
  await userEvent.click(within(cell).getByRole("button", { name: "Data Poisoning" }));
  await waitFor(() => expect(screen.queryByText(/coverage matrix/i)).not.toBeInTheDocument());
});

import { render, screen, waitFor } from "@testing-library/react";
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
  expect(screen.getByRole("heading", { name: /adversarial sandbox/i })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByRole("button", { name: "Data Poisoning" })).toBeInTheDocument());
  await waitFor(() => expect(screen.getByRole("heading", { name: "Data Poisoning" })).toBeInTheDocument());
});

test("shows an error hint when the list fails", async () => {
  vi.spyOn(api, "listAttacks").mockRejectedValue(new api.ApiError(0, "Failed to fetch"));
  render(<App />);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/backend/i));
});

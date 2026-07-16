import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";
import * as api from "../api";
import { SweepPanel } from "./SweepPanel";

afterEach(() => vi.restoreAllMocks());

const spec: api.SweepSpec = {
  x_knob: "epsilon", x_values: [0, 0.1], x_label: "Epsilon", y_label: "Confidence",
  attacked_metric: "Adversarial confidence", defended_metric: "Adversarial confidence",
};

async function* fakeStream() {
  yield { x: 0, attacked: 0.9, defended: 0.9 } as api.SweepPoint;
  yield { x: 0.1, attacked: 0.2, defended: 0.7 } as api.SweepPoint;
  yield { done: true } as api.SweepPoint;
}

test("running the sweep streams points into a chart", async () => {
  vi.spyOn(api, "streamSweep").mockReturnValue(fakeStream());
  render(<SweepPanel attackId="perturbation" spec={spec} params={{ mode: "fgsm" }} />);
  await userEvent.click(screen.getByRole("button", { name: /run sweep/i }));
  expect(await screen.findByText(/2 \/ 2/)).toBeInTheDocument();
  expect(document.querySelectorAll("polyline").length).toBe(2);
});

test("shows the x-axis label as guidance before running", () => {
  vi.spyOn(api, "streamSweep").mockReturnValue(fakeStream());
  render(<SweepPanel attackId="perturbation" spec={spec} params={{}} />);
  expect(screen.getByText(/Epsilon/)).toBeInTheDocument();
});

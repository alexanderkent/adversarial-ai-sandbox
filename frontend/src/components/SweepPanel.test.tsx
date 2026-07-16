import { render, screen, waitFor } from "@testing-library/react";
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

test("aborts the in-flight stream when the component unmounts", async () => {
  let captured: AbortSignal | undefined;
  async function* pending(_id: string, _params: api.Params, signal?: AbortSignal) {
    captured = signal;
    yield { x: 0, attacked: 0.9, defended: 0.9 } as api.SweepPoint;
    await new Promise<void>(() => {}); // stay in-flight forever
  }
  vi.spyOn(api, "streamSweep").mockImplementation(pending);
  const { unmount } = render(<SweepPanel attackId="perturbation" spec={spec} params={{}} />);
  await userEvent.click(screen.getByRole("button", { name: /run sweep/i }));
  expect(captured?.aborted).toBe(false);
  unmount();
  expect(captured?.aborted).toBe(true);
});

test("an aborted stream does not surface an error", async () => {
  let release!: () => void;
  const gate = new Promise<void>((r) => { release = r; });
  async function* aborting(_id: string, _params: api.Params, signal?: AbortSignal) {
    yield { x: 0, attacked: 0.9, defended: 0.9 } as api.SweepPoint;
    await gate; // suspend until the test triggers an abort
    if (signal?.aborted) throw new DOMException("aborted", "AbortError");
    yield { x: 0.1, attacked: 0.2, defended: 0.7 } as api.SweepPoint;
  }
  vi.spyOn(api, "streamSweep").mockImplementation(aborting);
  const { rerender } = render(<SweepPanel attackId="attack-a" spec={spec} params={{}} />);
  await userEvent.click(screen.getByRole("button", { name: /run sweep/i }));
  // switching attacks aborts the in-flight controller
  rerender(<SweepPanel attackId="attack-b" spec={spec} params={{}} />);
  release(); // generator resumes, sees aborted signal, throws AbortError
  await waitFor(() => expect(screen.getByRole("button", { name: /run sweep/i })).toBeEnabled());
  expect(screen.queryByRole("alert")).toBeNull();
  // the aborted stream's later points must not bleed onto the new attack's chart
  expect(document.querySelectorAll("circle").length).toBe(0);
});

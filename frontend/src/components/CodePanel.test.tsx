import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { CodePanel } from "./CodePanel";

const code = [{ label: "FGSM", language: "python", source: "def fgsm():\n    pass" }];

test("renders each snippet's label and source", () => {
  const { container } = render(<CodePanel code={code} />);
  expect(screen.getByText("FGSM")).toBeInTheDocument();
  expect(container.textContent).toContain("def fgsm");
});

test("shows a placeholder when there is no code", () => {
  render(<CodePanel code={[]} />);
  expect(screen.getByText(/no code/i)).toBeInTheDocument();
});

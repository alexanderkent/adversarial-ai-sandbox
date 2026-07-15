import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import type { RunResult } from "../api";
import { ArtifactPanel } from "./ArtifactPanel";

const result: RunResult = {
  figure: { kind: "figure", png_base64: "AAAA", caption: "cap" },
  metrics: [{ label: "Clean accuracy", value: 0.96, display: "96%" }],
  narrative: "Accuracy dropped.",
};

test("shows loading state", () => {
  render(<ArtifactPanel result={null} loading={true} error={null} />);
  expect(screen.getByText(/running/i)).toBeInTheDocument();
});

test("shows error state", () => {
  render(<ArtifactPanel result={null} loading={false} error="checkpoint missing" />);
  expect(screen.getByRole("alert")).toHaveTextContent("checkpoint missing");
});

test("renders image, caption, metric and narrative", () => {
  render(<ArtifactPanel result={result} loading={false} error={null} />);
  const img = screen.getByRole("img") as HTMLImageElement;
  expect(img.src).toContain("data:image/png;base64,AAAA");
  expect(screen.getByText("cap")).toBeInTheDocument();
  expect(screen.getByText("96%")).toBeInTheDocument();
  expect(screen.getByText("Accuracy dropped.")).toBeInTheDocument();
});

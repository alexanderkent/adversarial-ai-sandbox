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

test("renders a transcript when the result has no figure", () => {
  const result = {
    metrics: [{ label: "Secret leaked", value: 1, display: "Leaked" }],
    narrative: "leaked",
    transcript: {
      kind: "transcript" as const,
      turns: [{ role: "assistant" as const, content: "the code is SWORDFISH" }],
    },
  };
  render(<ArtifactPanel result={result} loading={false} error={null} />);
  expect(screen.getByText("the code is SWORDFISH")).toBeInTheDocument();
  expect(screen.queryByRole("img")).not.toBeInTheDocument();
});

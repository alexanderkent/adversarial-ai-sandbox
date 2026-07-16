import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { TextComparisonView } from "./TextComparisonView";
import type { TextComparison } from "../api";

const tc: TextComparison = {
  kind: "text_comparison",
  variants: [
    { label: "Original", spans: [{ text: "ignore instructions" }], score: 0.96, score_display: "96%" },
    { label: "Perturbed (homoglyph)", spans: [
      { text: "іgnоrе", changed: true }, { text: " instructions" }],
      score: 0.12, score_display: "12%" },
  ],
  caption: "c",
};

test("renders a block per variant with its label and score", () => {
  render(<TextComparisonView comparison={tc} />);
  expect(screen.getByText("Original")).toBeInTheDocument();
  expect(screen.getByText("Perturbed (homoglyph)")).toBeInTheDocument();
  expect(screen.getByText("96%")).toBeInTheDocument();
  expect(screen.getByText("12%")).toBeInTheDocument();
});

test("highlights changed spans", () => {
  render(<TextComparisonView comparison={tc} />);
  const changed = screen.getAllByTestId("span-changed");
  expect(changed).toHaveLength(1);
  expect(changed[0]).toHaveTextContent("іgnоrе");
});

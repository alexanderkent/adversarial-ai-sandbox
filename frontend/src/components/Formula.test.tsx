import { render } from "@testing-library/react";
import { expect, test } from "vitest";
import { Formula } from "./Formula";

test("renders a LaTeX string as KaTeX output", () => {
  const { container } = render(<Formula tex="x_{adv} = x + \\epsilon" />);
  expect(container.querySelector(".katex")).toBeTruthy();
});

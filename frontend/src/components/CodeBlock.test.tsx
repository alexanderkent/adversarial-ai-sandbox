import { render } from "@testing-library/react";
import { expect, test } from "vitest";
import { CodeBlock } from "./CodeBlock";

test("renders highlighted source that still contains the code text", () => {
  const { container } = render(<CodeBlock source={"def fgsm(model, x):\n    return x"} />);
  expect(container.textContent).toContain("def fgsm");
  expect(container.querySelector("code.hljs")).toBeTruthy();
});

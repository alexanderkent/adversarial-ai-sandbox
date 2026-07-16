import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { SweepChart } from "./SweepChart";

test("renders one polyline per series and the axis labels", () => {
  const { container } = render(
    <SweepChart
      points={[
        { x: 0, attacked: 0.9, defended: 0.9 },
        { x: 1, attacked: 0.2, defended: 0.7 },
      ]}
      xLabel="Epsilon"
      yLabel="Confidence"
      attackedLabel="Attacked"
      defendedLabel="Defended"
    />,
  );
  expect(container.querySelectorAll("polyline")).toHaveLength(2);
  expect(screen.getByText("Epsilon")).toBeInTheDocument();
  expect(screen.getByText("Confidence")).toBeInTheDocument();
});

test("omits the defended polyline when defendedLabel is null", () => {
  const { container } = render(
    <SweepChart
      points={[{ x: 0, attacked: 0.5 }]}
      xLabel="x" yLabel="y" attackedLabel="Attacked" defendedLabel={null}
    />,
  );
  expect(container.querySelectorAll("polyline")).toHaveLength(1);
});

import { useState } from "react";
import type { DecisionSurface } from "../api";

const W = 460;
const H = 400;
const M = 8;

export function DecisionSurfaceView({ surface }: { surface: DecisionSurface }) {
  const [active, setActive] = useState(0);
  const [hover, setHover] = useState<number | null>(null);
  const st = surface.states[active] ?? surface.states[0];
  const { domain, grid, resolution: R, points } = st;

  const iw = W - 2 * M;
  const ih = H - 2 * M;
  const px = (x: number) => M + ((x - domain.x_min) / (domain.x_max - domain.x_min || 1)) * iw;
  const py = (y: number) => M + ((domain.y_max - y) / (domain.y_max - domain.y_min || 1)) * ih;
  const cw = iw / R;
  const ch = ih / R;
  const cls = (v: number) => (v === 0 ? "var(--chart-attacked)" : "var(--chart-defended)");

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-3">
        <div role="group" aria-label="Model state" className="inline-flex rounded-lg border border-border p-0.5">
          {surface.states.map((s, i) => (
            <button
              key={s.title}
              type="button"
              aria-pressed={i === active}
              onClick={() => {
                setActive(i);
                setHover(null);
              }}
              className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                i === active ? "bg-primary text-on-primary" : "text-ink-muted hover:text-ink"
              }`}
            >
              {s.title}
            </button>
          ))}
        </div>
        <span className="text-xs tabular-nums text-ink-muted">
          Accuracy on true data: {Math.round(st.accuracy * 100)}%
        </span>
      </div>

      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full rounded-lg border border-border bg-surface"
        role="img"
        aria-label="Decision boundary"
      >
        {grid.map((row, r) =>
          row.map((v, c) => (
            <rect
              key={`${r}-${c}`}
              x={M + c * cw}
              y={M + r * ch}
              width={cw + 0.6}
              height={ch + 0.6}
              fill={cls(v)}
              opacity={0.18}
              style={{ transition: "fill 400ms" }}
            />
          )),
        )}

        {points.map((pt, i) =>
          pt.poison ? (
            <path
              key={i}
              data-testid="decision-point"
              data-poison="true"
              d={`M ${px(pt.x) - 4} ${py(pt.y) - 4} L ${px(pt.x) + 4} ${py(pt.y) + 4} M ${px(pt.x) + 4} ${py(pt.y) - 4} L ${px(pt.x) - 4} ${py(pt.y) + 4}`}
              stroke="var(--danger)"
              strokeWidth={2}
              strokeLinecap="round"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
          ) : (
            <circle
              key={i}
              data-testid="decision-point"
              data-poison="false"
              cx={px(pt.x)}
              cy={py(pt.y)}
              r={3.2}
              fill={cls(pt.label)}
              stroke="var(--ink)"
              strokeWidth={0.6}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
          ),
        )}

        {hover != null && points[hover] && (
          <g data-testid="decision-tooltip" pointerEvents="none">
            <rect
              x={Math.min(px(points[hover].x) + 6, W - 174)}
              y={Math.max(py(points[hover].y) - 24, 2)}
              width={168}
              height={20}
              rx={4}
              fill="var(--surface)"
              stroke="var(--border)"
            />
            <text
              x={Math.min(px(points[hover].x) + 12, W - 168)}
              y={Math.max(py(points[hover].y) - 10, 16)}
              fontSize={9}
              fill="var(--ink)"
            >
              ({points[hover].x.toFixed(1)}, {points[hover].y.toFixed(1)}) · class {points[hover].label}
              {points[hover].poison ? " · poisoned" : ""}
            </text>
          </g>
        )}
      </svg>

      {surface.caption && <p className="text-xs text-ink-subtle">{surface.caption}</p>}
    </div>
  );
}

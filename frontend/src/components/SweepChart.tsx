import type { SweepPoint } from "../api";

const W = 420, H = 260, M = { t: 12, r: 12, b: 40, l: 44 };
const ATTACKED = "#6366f1"; // indigo-500
const DEFENDED = "#10b981"; // emerald-500

interface SweepChartProps {
  points: SweepPoint[];
  xLabel: string;
  yLabel: string;
  attackedLabel: string;
  defendedLabel: string | null;
}

export function SweepChart({ points, xLabel, yLabel, defendedLabel }: SweepChartProps) {
  const valid = points.filter((p) => typeof p.x === "number" && p.error === undefined);
  const xs = valid.map((p) => p.x as number);
  const xMin = Math.min(...xs, 0), xMax = Math.max(...xs, 1);
  const px = (x: number) => M.l + ((x - xMin) / (xMax - xMin || 1)) * (W - M.l - M.r);
  const py = (y: number) => M.t + (1 - Math.max(0, Math.min(1, y))) * (H - M.t - M.b);

  const line = (key: "attacked" | "defended") =>
    valid
      .filter((p) => typeof p[key] === "number")
      .map((p) => `${px(p.x as number)},${py(p[key] as number)}`)
      .join(" ");

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${yLabel} vs ${xLabel}`}>
      {/* axes */}
      <line x1={M.l} y1={M.t} x2={M.l} y2={H - M.b} stroke="#cbd5e1" />
      <line x1={M.l} y1={H - M.b} x2={W - M.r} y2={H - M.b} stroke="#cbd5e1" />
      {/* y ticks at 0/0.5/1 */}
      {[0, 0.5, 1].map((t) => (
        <g key={t}>
          <text x={M.l - 6} y={py(t) + 4} textAnchor="end" className="fill-slate-500 text-[10px]">
            {t}
          </text>
          <line x1={M.l} y1={py(t)} x2={W - M.r} y2={py(t)} stroke="#f1f5f9" />
        </g>
      ))}
      {/* series */}
      <polyline fill="none" stroke={ATTACKED} strokeWidth={2} points={line("attacked")} />
      {defendedLabel && (
        <polyline fill="none" stroke={DEFENDED} strokeWidth={2} points={line("defended")} />
      )}
      {valid.map((p, i) => (
        <g key={`${p.x}-${i}`}>
          {typeof p.attacked === "number" && (
            <circle cx={px(p.x as number)} cy={py(p.attacked)} r={3} fill={ATTACKED} />
          )}
          {defendedLabel && typeof p.defended === "number" && (
            <circle cx={px(p.x as number)} cy={py(p.defended)} r={3} fill={DEFENDED} />
          )}
        </g>
      ))}
      {/* axis labels */}
      <text x={(W + M.l) / 2} y={H - 6} textAnchor="middle" className="fill-slate-600 text-[11px]">
        {xLabel}
      </text>
      <text x={12} y={H / 2} textAnchor="middle" transform={`rotate(-90 12 ${H / 2})`} className="fill-slate-600 text-[11px]">
        {yLabel}
      </text>
    </svg>
  );
}

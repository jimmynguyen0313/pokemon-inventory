import React, { useEffect, useMemo, useRef, useState } from 'react';
import { longDate, money, moneyCompact, shortMonth, signedPct } from '../format';

const RANGES = [
  { label: '6M', months: 6 },
  { label: '1Y', months: 12 },
  { label: '2Y', months: 24 },
];
const HEIGHT = 260;
const PAD = { top: 16, right: 12, bottom: 28, left: 56 };

function useWidth(ref) {
  const [width, setWidth] = useState(640);
  useEffect(() => {
    if (!ref.current || typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(([entry]) => setWidth(Math.max(280, entry.contentRect.width)));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, [ref]);
  return width;
}

function niceTicks(min, max, count = 4) {
  const span = max - min || 1;
  const step = 10 ** Math.floor(Math.log10(span / count));
  const nice = [1, 2, 2.5, 5, 10].map((m) => m * step).find((s) => span / s <= count) || step * 10;
  const ticks = [];
  for (let v = Math.floor(min / nice) * nice; v <= max + 1e-9; v += nice) ticks.push(v);
  return ticks;
}

export default function ValueChart({ points, months, onMonthsChange, loading }) {
  const wrap = useRef(null);
  const width = useWidth(wrap);
  const [hover, setHover] = useState(null);

  const chart = useMemo(() => {
    if (!points.length) return null;
    const values = points.flatMap((p) => [p.market_value, p.cost_basis]);
    const ticks = niceTicks(Math.min(...values) * 0.95, Math.max(...values) * 1.03);
    const lo = ticks[0];
    const hi = ticks[ticks.length - 1];
    const w = width - PAD.left - PAD.right;
    const h = HEIGHT - PAD.top - PAD.bottom;
    const x = (i) => PAD.left + (points.length === 1 ? w / 2 : (i / (points.length - 1)) * w);
    const y = (v) => PAD.top + h - ((v - lo) / (hi - lo || 1)) * h;
    const line = (key) => points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p[key]).toFixed(1)}`).join('');
    const area = `${line('market_value')}L${x(points.length - 1)},${PAD.top + h}L${x(0)},${PAD.top + h}Z`;
    const labelEvery = Math.ceil(points.length / Math.max(2, Math.floor(w / 70)));
    return { ticks, x, y, area, value: line('market_value'), cost: line('cost_basis'), labelEvery, w };
  }, [points, width]);

  const first = points[0];
  const last = points[points.length - 1];
  const change = first && first.market_value ? ((last.market_value - first.market_value) / first.market_value) * 100 : null;

  const onMove = (e) => {
    if (!chart) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const rel = (e.clientX - rect.left - PAD.left) / chart.w;
    setHover(Math.min(points.length - 1, Math.max(0, Math.round(rel * (points.length - 1)))));
  };

  const active = hover != null ? points[hover] : null;

  return (
    <section className="card chart" aria-label="Portfolio value over time">
      <div className="card__head">
        <div>
          <h2>Value over time</h2>
          {change != null && (
            <p className="muted">
              <span className={change >= 0 ? 'tone-up' : 'tone-down'}>{signedPct(change)}</span> over this period
            </p>
          )}
        </div>
        <div className="segmented" role="group" aria-label="Time range">
          {RANGES.map((r) => (
            <button
              key={r.label}
              type="button"
              aria-pressed={months === r.months}
              onClick={() => onMonthsChange(r.months)}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <div className="chart__legend">
        <span><i className="swatch swatch--value" />Market value</span>
        <span><i className="swatch swatch--cost" />Cost basis</span>
      </div>

      <div ref={wrap} className="chart__plot" style={{ height: HEIGHT }}>
        {!chart ? (
          !loading && <p className="muted empty">Add items to see your portfolio's value over time.</p>
        ) : (
          <svg
            width={width}
            height={HEIGHT}
            role="img"
            aria-label={`Market value from ${money(first.market_value)} to ${money(last.market_value)}`}
            onMouseMove={onMove}
            onMouseLeave={() => setHover(null)}
          >
            <defs>
              <linearGradient id="valueFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.28" />
                <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
              </linearGradient>
            </defs>
            {chart.ticks.map((t) => (
              <g key={t}>
                <line x1={PAD.left} x2={width - PAD.right} y1={chart.y(t)} y2={chart.y(t)} className="grid" />
                <text x={PAD.left - 10} y={chart.y(t)} className="axis" textAnchor="end" dominantBaseline="middle">
                  {moneyCompact(t)}
                </text>
              </g>
            ))}
            {points.map((p, i) =>
              i % chart.labelEvery === 0 || i === points.length - 1 ? (
                <text key={p.date} x={chart.x(i)} y={HEIGHT - 8} className="axis" textAnchor="middle">
                  {i === points.length - 1 ? 'Now' : shortMonth(p.date)}
                </text>
              ) : null
            )}
            <path d={chart.area} fill="url(#valueFill)" />
            <path d={chart.cost} className="line line--cost" />
            <path d={chart.value} className="line line--value" />
            {active && (
              <g>
                <line x1={chart.x(hover)} x2={chart.x(hover)} y1={PAD.top} y2={HEIGHT - PAD.bottom} className="crosshair" />
                <circle cx={chart.x(hover)} cy={chart.y(active.market_value)} r="4.5" className="dot" />
              </g>
            )}
          </svg>
        )}
        {active && (
          <div
            className="tooltip"
            style={{ left: Math.min(Math.max(chart.x(hover), 90), width - 90) }}
          >
            <strong>{longDate(active.date)}</strong>
            <span>Value {money(active.market_value)}</span>
            <span className="muted">Cost {money(active.cost_basis)}</span>
          </div>
        )}
      </div>
    </section>
  );
}

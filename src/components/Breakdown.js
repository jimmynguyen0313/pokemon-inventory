import React, { useState } from 'react';
import { moneyWhole, signedPct } from '../format';

const PALETTE = ['#7c9cff', '#5fd3a2', '#f5c26b', '#f2777a', '#c792ea', '#5cc8e8', '#8a8f9c'];

export function Allocation({ summary }) {
  const [view, setView] = useState('by_type');
  const slices = summary[view];

  return (
    <section className="card" aria-label="Allocation">
      <div className="card__head">
        <h2>Allocation</h2>
        <div className="segmented" role="group" aria-label="Group by">
          <button type="button" aria-pressed={view === 'by_type'} onClick={() => setView('by_type')}>Type</button>
          <button type="button" aria-pressed={view === 'by_set'} onClick={() => setView('by_set')}>Set</button>
        </div>
      </div>
      {slices.length === 0 ? (
        <p className="muted">Nothing here yet.</p>
      ) : (
        <>
          <div className="stack" role="img" aria-label={slices.map((s) => `${s.label} ${s.share}%`).join(', ')}>
            {slices.map((s, i) => (
              <span key={s.label} style={{ width: `${s.share}%`, background: PALETTE[i % PALETTE.length] }} />
            ))}
          </div>
          <ul className="legend-list">
            {slices.map((s, i) => (
              <li key={s.label}>
                <i className="swatch" style={{ background: PALETTE[i % PALETTE.length] }} />
                <span className="legend-list__label">{s.label}</span>
                <span className="muted">{moneyWhole(s.value)}</span>
                <span className="legend-list__share">{s.share.toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

export function Movers({ summary }) {
  const groups = [
    { title: 'Top gainers', rows: summary.top_gainers },
    { title: 'Top decliners', rows: summary.top_losers },
  ];
  return (
    <section className="card" aria-label="Top movers">
      <div className="card__head"><h2>Movers</h2></div>
      {groups.map((g) => (
        <div key={g.title} className="movers">
          <h3>{g.title}</h3>
          {g.rows.length === 0 ? (
            <p className="muted small">None</p>
          ) : (
            <ul>
              {g.rows.map((r) => (
                <li key={r.item_id}>
                  <span className="truncate">{r.name.replace(/^Pokémon /, '')}</span>
                  <span className={`pill ${r.gain_pct >= 0 ? 'pill--up' : 'pill--down'}`}>{signedPct(r.gain_pct)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </section>
  );
}

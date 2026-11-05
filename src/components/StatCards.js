import React from 'react';
import { longDate, money, signedMoney, signedPct, trend } from '../format';

export default function StatCards({ summary }) {
  const s = summary;
  const t = trend(s.unrealized_gain);
  const cards = [
    { label: 'Market value', value: money(s.market_value), note: `as of ${longDate(s.as_of)}` },
    { label: 'Cost basis', value: money(s.cost_basis), note: 'total paid' },
    {
      label: 'Unrealized gain',
      value: signedMoney(s.unrealized_gain),
      note: signedPct(s.unrealized_gain_pct),
      tone: t,
    },
    { label: 'Holdings', value: s.holdings.toLocaleString(), note: `${s.units.toLocaleString()} sealed units` },
  ];

  return (
    <section className="stats" aria-label="Portfolio summary">
      {cards.map((c) => (
        <div key={c.label} className="card stat">
          <div className="stat__label">{c.label}</div>
          <div className={`stat__value ${c.tone ? `tone-${c.tone}` : ''}`}>{c.value}</div>
          <div className={`stat__note ${c.tone ? `tone-${c.tone}` : ''}`}>{c.note}</div>
        </div>
      ))}
    </section>
  );
}

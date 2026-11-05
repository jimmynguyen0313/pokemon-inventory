import React, { useMemo, useState } from 'react';
import { longDate, money, signedMoney, signedPct, trend } from '../format';
import ProductThumb from './ProductThumb';

const COLUMNS = [
  { key: 'name', label: 'Product', align: 'left' },
  { key: 'quantity', label: 'Qty' },
  { key: 'purchase_price', label: 'Paid / unit' },
  { key: 'market_value', label: 'Market / unit' },
  { key: 'market_total', label: 'Value' },
  { key: 'gain', label: 'Gain' },
  { key: 'gain_pct', label: 'Return' },
];

export function sortItems(items, key, dir) {
  const sign = dir === 'asc' ? 1 : -1;
  return [...items].sort((a, b) => {
    const av = a[key] ?? -Infinity;
    const bv = b[key] ?? -Infinity;
    if (typeof av === 'string') return av.localeCompare(bv) * sign;
    return (av - bv) * sign;
  });
}

export default function HoldingsTable({ items, onDelete, onAdd }) {
  const [sort, setSort] = useState({ key: 'market_total', dir: 'desc' });
  const [query, setQuery] = useState('');

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = q
      ? items.filter((i) => `${i.name} ${i.set_name} ${i.category_name || ''}`.toLowerCase().includes(q))
      : items;
    return sortItems(filtered, sort.key, sort.dir);
  }, [items, query, sort]);

  const toggle = (key) =>
    setSort((s) => (s.key === key ? { key, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: key === 'name' ? 'asc' : 'desc' }));

  return (
    <section className="card holdings" aria-label="Holdings">
      <div className="card__head">
        <div>
          <h2>Holdings</h2>
          <p className="muted">{items.length} {items.length === 1 ? 'item' : 'items'}</p>
        </div>
        <div className="holdings__tools">
          <input
            type="search"
            className="input"
            placeholder="Filter holdings"
            aria-label="Filter holdings"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="button" className="btn btn--primary" onClick={onAdd}>+ Add item</button>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <p>No items yet.</p>
          <button type="button" className="btn btn--primary" onClick={onAdd}>Add your first item</button>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {COLUMNS.map((c) => (
                  <th
                    key={c.key}
                    className={c.align === 'left' ? 'left' : ''}
                    aria-sort={sort.key === c.key ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}
                  >
                    <button type="button" onClick={() => toggle(c.key)}>
                      {c.label}
                      <span className="sort-arrow" aria-hidden="true">
                        {sort.key === c.key ? (sort.dir === 'asc' ? '↑' : '↓') : ''}
                      </span>
                    </button>
                  </th>
                ))}
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {rows.map((i) => (
                <tr key={i.id}>
                  <td className="left">
                    <div className="product-cell">
                      <ProductThumb src={i.images_url} name={i.name} setName={i.set_name} productType={i.product_type} />
                      <div>
                        <div className="product-cell__name">{i.name.replace(/^Pokémon /, '')}</div>
                        <div className="muted small">
                          {i.category_name ? `${i.category_name} · ` : ''}bought {longDate(i.purchase_date)}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td data-label="Qty">{i.quantity}</td>
                  <td data-label="Paid / unit">{money(i.purchase_price)}</td>
                  <td data-label="Market / unit">{i.market_value != null ? money(i.market_value) : '—'}</td>
                  <td data-label="Value" className="strong">{money(i.market_total)}</td>
                  <td data-label="Gain" className={`tone-${trend(i.gain)}`}>{signedMoney(i.gain)}</td>
                  <td data-label="Return">
                    <span className={`pill pill--${trend(i.gain_pct) === 'down' ? 'down' : 'up'}`}>{signedPct(i.gain_pct)}</span>
                  </td>
                  <td className="actions">
                    <button
                      type="button"
                      className="icon-btn"
                      aria-label={`Delete ${i.name}`}
                      title="Delete"
                      onClick={() => onDelete(i)}
                    >
                      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3" /></svg>
                    </button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr><td colSpan={COLUMNS.length + 1} className="muted">No holdings match “{query}”.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

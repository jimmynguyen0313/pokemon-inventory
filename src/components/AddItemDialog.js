import React, { useEffect, useRef, useState } from 'react';
import { api } from '../api';
import { money } from '../format';
import ProductThumb from './ProductThumb';

const today = () => new Date().toISOString().slice(0, 10);

export default function AddItemDialog({ open, onClose, onAdded }) {
  const dialog = useRef(null);
  const searchInput = useRef(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [product, setProduct] = useState(null);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({ quantity: 1, price: '', date: today(), category: '' });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  // Open/close the native <dialog>, and reset state each time it opens.
  useEffect(() => {
    const d = dialog.current;
    if (!d) return;
    if (open && !d.open) {
      setQuery('');
      setResults([]);
      setProduct(null);
      setError('');
      setForm({ quantity: 1, price: '', date: today(), category: '' });
      if (typeof d.showModal === 'function') d.showModal();
      else d.setAttribute('open', '');
      setTimeout(() => searchInput.current && searchInput.current.focus(), 0);
      api.categories().then(setCategories).catch(() => setCategories([]));
    } else if (!open && d.open) {
      if (typeof d.close === 'function') d.close();
      else d.removeAttribute('open');
    }
  }, [open]);

  // Debounced product search; shows the whole catalog when the box is empty.
  useEffect(() => {
    if (!open || product) return undefined;
    setSearching(true);
    const timer = setTimeout(() => {
      api
        .search(query.trim())
        .then(setResults)
        .catch(() => setResults([]))
        .finally(() => setSearching(false));
    }, 200);
    return () => clearTimeout(timer);
  }, [query, open, product]);

  const choose = (p) => {
    setProduct(p);
    setForm((f) => ({ ...f, price: p.market_value != null ? String(p.market_value) : '' }));
  };

  const submit = async (e) => {
    e.preventDefault();
    const price = parseFloat(form.price);
    const quantity = parseInt(form.quantity, 10);
    if (!(quantity > 0)) return setError('Quantity must be at least 1.');
    if (!(price >= 0)) return setError('Enter the price you paid per unit.');
    setSaving(true);
    setError('');
    try {
      await api.addItem({
        product_id: product.id,
        quantity,
        purchase_price: price,
        purchase_date: form.date || null,
        category_id: form.category ? parseInt(form.category, 10) : null,
      });
      onAdded(`Added ${quantity}× ${product.name.replace(/^Pokémon /, '')}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <dialog
      ref={dialog}
      className="dialog"
      aria-labelledby="add-title"
      onCancel={(e) => { e.preventDefault(); onClose(); }}
      onClick={(e) => { if (e.target === dialog.current) onClose(); }}
    >
      <div className="dialog__body">
        <div className="dialog__head">
          <h2 id="add-title">{product ? 'Add to collection' : 'Choose a product'}</h2>
          <button type="button" className="icon-btn" aria-label="Close" onClick={onClose}>×</button>
        </div>

        {!product ? (
          <>
            <input
              ref={searchInput}
              type="search"
              className="input"
              placeholder="Search by set or product, e.g. Evolving Skies"
              aria-label="Search products"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <ul className="results" aria-busy={searching}>
              {results.map((p) => (
                <li key={p.id}>
                  <button type="button" className="result" onClick={() => choose(p)}>
                    <ProductThumb src={p.images_url} name={p.name} setName={p.set_name} productType={p.product_type} size={40} />
                    <span className="result__text">
                      <span className="result__name">{p.name.replace(/^Pokémon /, '')}</span>
                      <span className="muted small">{p.product_type} · {p.set_name}</span>
                    </span>
                    <span className="result__price">{p.market_value != null ? money(p.market_value) : '—'}</span>
                  </button>
                </li>
              ))}
              {!searching && results.length === 0 && <li className="muted small pad">No products match “{query}”.</li>}
            </ul>
          </>
        ) : (
          <form onSubmit={submit} className="add-form">
            <div className="chosen">
              <ProductThumb src={product.images_url} name={product.name} setName={product.set_name} productType={product.product_type} size={48} />
              <div className="result__text">
                <span className="result__name">{product.name.replace(/^Pokémon /, '')}</span>
                <span className="muted small">Market price {product.market_value != null ? money(product.market_value) : 'unknown'}</span>
              </div>
              <button type="button" className="btn btn--ghost" onClick={() => setProduct(null)}>Change</button>
            </div>

            <div className="fields">
              <label>
                <span>Quantity</span>
                <input className="input" type="number" min="1" step="1" value={form.quantity} onChange={set('quantity')} required />
              </label>
              <label>
                <span>Paid per unit ($)</span>
                <input className="input" type="number" min="0" step="0.01" value={form.price} onChange={set('price')} required />
              </label>
              <label>
                <span>Purchase date</span>
                <input className="input" type="date" max={today()} value={form.date} onChange={set('date')} />
              </label>
              <label>
                <span>Category</span>
                <select className="input" value={form.category} onChange={set('category')}>
                  <option value="">None</option>
                  {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </label>
            </div>

            {error && <p className="form-error" role="alert">{error}</p>}
            <div className="dialog__actions">
              <button type="button" className="btn btn--ghost" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn--primary" disabled={saving}>{saving ? 'Adding…' : 'Add to collection'}</button>
            </div>
          </form>
        )}
      </div>
    </dialog>
  );
}

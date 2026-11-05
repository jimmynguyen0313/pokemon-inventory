import React, { useCallback, useEffect, useRef, useState } from 'react';
import './App.css';
import { api } from './api';
import StatCards from './components/StatCards';
import ValueChart from './components/ValueChart';
import { Allocation, Movers } from './components/Breakdown';
import HoldingsTable from './components/HoldingsTable';
import AddItemDialog from './components/AddItemDialog';

const SLOW_AFTER_MS = 4000;

export default function App() {
  const [summary, setSummary] = useState(null);
  const [items, setItems] = useState([]);
  const [history, setHistory] = useState(null);
  const [months, setMonths] = useState(12);
  const [status, setStatus] = useState('loading'); // loading | ready | error
  const [slow, setSlow] = useState(false);
  const [adding, setAdding] = useState(false);
  const [toast, setToast] = useState('');
  const toastTimer = useRef(null);

  const load = useCallback(async () => {
    const [s, i] = await Promise.all([api.summary(), api.items()]);
    setSummary(s);
    setItems(i);
  }, []);

  // First load; the free-tier API sleeps when idle, so say so if it's slow.
  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), SLOW_AFTER_MS);
    load()
      .then(() => setStatus('ready'))
      .catch(() => setStatus('error'))
      .finally(() => clearTimeout(timer));
    return () => clearTimeout(timer);
  }, [load]);

  useEffect(() => {
    if (status !== 'ready') return;
    api.history(months).then(setHistory).catch(() => setHistory([]));
  }, [months, status, items]);

  useEffect(() => () => clearTimeout(toastTimer.current), []);

  const notify = (message) => {
    setToast(message);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(''), 3500);
  };

  const refresh = () => load().catch(() => notify('Could not refresh. Try again in a moment.'));

  const handleAdded = (message) => {
    setAdding(false);
    notify(message);
    refresh();
  };

  const handleDelete = async (item) => {
    if (!window.confirm(`Remove ${item.name} from your collection?`)) return;
    try {
      await api.deleteItem(item.id);
      notify('Item removed');
      refresh();
    } catch (err) {
      notify(err.message);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__inner">
          <div className="brand">
            <span className="brand__mark" aria-hidden="true" />
            <span>Sealed Inventory</span>
          </div>
          <span className="badge" title="Prices and holdings are sample data">Demo data</span>
        </div>
      </header>

      <main className="main">
        <div className="page-title">
          <h1>Portfolio</h1>
          <p className="muted">Track sealed Pokémon TCG products, what you paid, and what they're worth today.</p>
        </div>

        {status === 'loading' && (
          <div className="loading" role="status">
            <div className="skeleton-row">{[0, 1, 2, 3].map((k) => <div key={k} className="card skeleton" />)}</div>
            <div className="card skeleton skeleton--tall" />
            {slow && <p className="muted center">Waking up the demo server. The free tier sleeps when idle, so this can take up to 30 seconds.</p>}
          </div>
        )}

        {status === 'error' && (
          <div className="card error-state" role="alert">
            <h2>Can't reach the API</h2>
            <p className="muted">The backend may be starting up or offline. Refresh the page in a moment.</p>
            <button type="button" className="btn btn--primary" onClick={() => window.location.reload()}>Retry</button>
          </div>
        )}

        {status === 'ready' && summary && (
          <>
            <StatCards summary={summary} />
            <ValueChart points={history || []} loading={history === null} months={months} onMonthsChange={setMonths} />
            <div className="grid-2">
              <Allocation summary={summary} />
              <Movers summary={summary} />
            </div>
            <HoldingsTable items={items} onDelete={handleDelete} onAdd={() => setAdding(true)} />
          </>
        )}
      </main>

      {status !== 'loading' && (
        <footer className="footer">
          Pokémon is a trademark of The Pokémon Company International. This project is not affiliated with it.
          Demo prices are illustrative.
        </footer>
      )}

      <AddItemDialog open={adding} onClose={() => setAdding(false)} onAdded={handleAdded} />
      <div className={`toast ${toast ? 'toast--show' : ''}`} role="status" aria-live="polite">{toast}</div>
    </div>
  );
}

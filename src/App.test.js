import { act, fireEvent, render, screen, within } from '@testing-library/react';
import App from './App';
import { sortItems } from './components/HoldingsTable';
import { signedMoney, signedPct, trend } from './format';

const SUMMARY = {
  market_value: 1250,
  cost_basis: 1000,
  unrealized_gain: 250,
  unrealized_gain_pct: 25,
  holdings: 2,
  units: 3,
  by_type: [{ label: 'Booster Box', value: 1000, share: 80 }, { label: 'Elite Trainer Box', value: 250, share: 20 }],
  by_set: [{ label: 'Jungle', value: 1000, share: 80 }, { label: 'Crown Zenith', value: 250, share: 20 }],
  top_gainers: [{ item_id: 1, name: 'Pokémon Jungle Set Booster Box', gain: 300, gain_pct: 42.86 }],
  top_losers: [{ item_id: 2, name: 'Pokémon Crown Zenith Elite Trainer Box', gain: -50, gain_pct: -16.67 }],
  as_of: '2026-11-05',
};

const ITEMS = [
  {
    id: 1, name: 'Pokémon Jungle Set Booster Box', set_name: 'Jungle', product_type: 'Booster Box',
    quantity: 1, purchase_price: 700, market_value: 1000, market_total: 1000, gain: 300, gain_pct: 42.86,
    purchase_date: '2025-01-03', category_name: 'Long-term hold', images_url: null,
  },
  {
    id: 2, name: 'Pokémon Crown Zenith Elite Trainer Box', set_name: 'Crown Zenith', product_type: 'Elite Trainer Box',
    quantity: 2, purchase_price: 150, market_value: 125, market_total: 250, gain: -50, gain_pct: -16.67,
    purchase_date: '2025-06-01', category_name: null, images_url: null,
  },
];

const HISTORY = [
  { date: '2026-10-01', market_value: 1100, cost_basis: 1000 },
  { date: '2026-11-05', market_value: 1250, cost_basis: 1000 },
];

function mockApi(overrides = {}) {
  const routes = { '/analytics/summary': SUMMARY, '/items': ITEMS, '/analytics/history': HISTORY, ...overrides };
  global.fetch = jest.fn((url) => {
    const path = Object.keys(routes).sort((a, b) => b.length - a.length).find((p) => url.includes(p));
    const body = path ? routes[path] : [];
    return Promise.resolve({ ok: !(body instanceof Error), status: 500, json: () => Promise.resolve(body) });
  });
}

async function renderApp() {
  await act(async () => {
    render(<App />);
  });
}

afterEach(() => jest.resetAllMocks());

test('shows portfolio totals and gain', async () => {
  mockApi();
  await renderApp();
  expect(screen.getByText('$1,250.00')).toBeInTheDocument();
  expect(screen.getByText('+$250.00')).toBeInTheDocument();
  expect(screen.getByText('+25.0%')).toBeInTheDocument();
  expect(screen.getByText('3 sealed units')).toBeInTheDocument();
});

test('lists holdings with gain and return, largest value first', async () => {
  mockApi();
  await renderApp();
  const rows = within(screen.getByRole('table')).getAllByRole('row').slice(1);
  expect(rows).toHaveLength(2);
  expect(within(rows[0]).getByText('Jungle Set Booster Box')).toBeInTheDocument();
  expect(within(rows[1]).getByText('−$50.00')).toBeInTheDocument();
});

test('filters holdings by text', async () => {
  mockApi();
  await renderApp();
  fireEvent.change(screen.getByLabelText('Filter holdings'), { target: { value: 'crown' } });
  const rows = within(screen.getByRole('table')).getAllByRole('row').slice(1);
  expect(rows).toHaveLength(1);
  expect(within(rows[0]).getByText(/Crown Zenith/)).toBeInTheDocument();
});

test('shows an empty state when there are no holdings', async () => {
  mockApi({ '/items': [], '/analytics/history': [] });
  await renderApp();
  expect(screen.getByText('No items yet.')).toBeInTheDocument();
});

test('shows an error when the API is unreachable', async () => {
  global.fetch = jest.fn(() => Promise.reject(new Error('offline')));
  await renderApp();
  expect(screen.getByRole('alert')).toHaveTextContent("Can't reach the API");
});

test('sortItems orders numbers and strings in both directions', () => {
  expect(sortItems(ITEMS, 'gain_pct', 'desc').map((i) => i.id)).toEqual([1, 2]);
  expect(sortItems(ITEMS, 'gain_pct', 'asc').map((i) => i.id)).toEqual([2, 1]);
  expect(sortItems(ITEMS, 'name', 'asc').map((i) => i.id)).toEqual([2, 1]);
});

test('format helpers', () => {
  expect(signedMoney(12.5)).toBe('+$12.50');
  expect(signedMoney(-3)).toBe('−$3.00');
  expect(signedPct(null)).toBe('—');
  expect(signedPct(-16.67)).toBe('−16.7%');
  expect([trend(5), trend(-1), trend(0)]).toEqual(['up', 'down', 'flat']);
});

test('adds an item through the dialog', async () => {
  mockApi({
    '/products/search': [{ id: 'jungle', name: 'Pokémon Jungle Set Booster Box', product_type: 'Booster Box', set_name: 'Jungle', market_value: 1000 }],
    '/categories': [{ id: 7, name: 'Vault' }],
  });
  await renderApp();
  fireEvent.click(screen.getByRole('button', { name: '+ Add item' }));
  const dialog = screen.getByRole('dialog', { hidden: true });
  fireEvent.change(within(dialog).getByLabelText('Search products'), { target: { value: 'jungle' } });
  const result = await within(dialog).findByRole('button', { name: /Jungle Set Booster Box/, hidden: true });
  fireEvent.click(result);

  // Paid price is prefilled from the market price; change quantity, category and price.
  expect(within(dialog).getByLabelText('Paid per unit ($)')).toHaveValue(1000);
  fireEvent.change(within(dialog).getByLabelText('Quantity'), { target: { value: '2' } });
  fireEvent.change(within(dialog).getByLabelText('Paid per unit ($)'), { target: { value: '650' } });
  await within(dialog).findByRole('option', { name: 'Vault', hidden: true });
  fireEvent.change(within(dialog).getByLabelText('Category'), { target: { value: '7' } });
  await act(async () => {
    fireEvent.click(within(dialog).getByRole('button', { name: 'Add to collection', hidden: true }));
  });

  const post = global.fetch.mock.calls.find(([, options]) => options && options.method === 'POST');
  expect(JSON.parse(post[1].body)).toMatchObject({ product_id: 'jungle', quantity: 2, purchase_price: 650, category_id: 7 });
  expect(screen.getByText('Added 2× Jungle Set Booster Box')).toBeInTheDocument();
});

test('validates the add form', async () => {
  mockApi({ '/products/search': [{ id: 'x', name: 'Pokémon X Box', product_type: 'Booster Box', set_name: 'X', market_value: null }] });
  await renderApp();
  fireEvent.click(screen.getByRole('button', { name: '+ Add item' }));
  const dialog = screen.getByRole('dialog', { hidden: true });
  fireEvent.click(await within(dialog).findByRole('button', { name: /X Box/, hidden: true }));
  fireEvent.change(within(dialog).getByLabelText('Quantity'), { target: { value: '0' } });
  fireEvent.submit(within(dialog).getByLabelText('Quantity').closest('form'));
  expect(within(dialog).getByRole('alert', { hidden: true })).toHaveTextContent('Quantity must be at least 1.');
});

test('deletes a holding after confirmation', async () => {
  mockApi({ '/items/1': { status: 'deleted', item_id: 1 } });
  window.confirm = jest.fn(() => true);
  await renderApp();
  await act(async () => {
    fireEvent.click(screen.getByRole('button', { name: /Delete Pokémon Jungle/ }));
  });
  expect(window.confirm).toHaveBeenCalled();
  expect(global.fetch.mock.calls.some(([url, options]) => url.endsWith('/items/1') && options.method === 'DELETE')).toBe(true);
  expect(screen.getByText('Item removed')).toBeInTheDocument();
});

test('changes the chart range', async () => {
  mockApi();
  await renderApp();
  await act(async () => {
    fireEvent.click(screen.getByRole('button', { name: '2Y' }));
  });
  expect(global.fetch.mock.calls.some(([url]) => url.includes('/analytics/history?months=24'))).toBe(true);
  expect(screen.getByRole('button', { name: '2Y' })).toHaveAttribute('aria-pressed', 'true');
});

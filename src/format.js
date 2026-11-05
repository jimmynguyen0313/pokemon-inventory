const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const currencyWhole = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const compact = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 1 });

export const money = (n) => currency.format(n ?? 0);
export const moneyWhole = (n) => currencyWhole.format(n ?? 0);
export const moneyCompact = (n) => compact.format(n ?? 0);

/** "+$12.50" / "−$3.00" — uses a real minus sign so columns align. */
export const signedMoney = (n) => `${n >= 0 ? '+' : '−'}${currency.format(Math.abs(n ?? 0))}`;

export const signedPct = (n) => (n == null ? '—' : `${n >= 0 ? '+' : '−'}${Math.abs(n).toFixed(1)}%`);

export const trend = (n) => (n == null || n === 0 ? 'flat' : n > 0 ? 'up' : 'down');

export const shortMonth = (iso) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('en-US', { month: 'short', year: '2-digit' });

export const longDate = (iso) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

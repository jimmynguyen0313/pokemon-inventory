import { API_BASE } from './config';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data && (data.detail || data.error);
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${response.status})`);
  }
  return data;
}

export const api = {
  summary: () => request('/analytics/summary'),
  history: (months) => request(`/analytics/history?months=${months}`),
  items: () => request('/items'),
  categories: () => request('/categories'),
  search: (query) => request(`/products/search?name=${encodeURIComponent(query)}`),
  addItem: (body) =>
    request('/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  deleteItem: (id) => request(`/items/${id}`, { method: 'DELETE' }),
};

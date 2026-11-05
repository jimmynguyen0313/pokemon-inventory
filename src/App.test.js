import { act, render, screen } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve([]) })
  );
});

afterEach(() => {
  jest.resetAllMocks();
});

test('renders the app header', async () => {
  await act(async () => {
    render(<App />);
  });
  expect(screen.getByRole('heading', { name: /pokemon sealed inventory/i })).toBeInTheDocument();
});

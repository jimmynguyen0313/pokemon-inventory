// Base URL for the backend API. Set REACT_APP_API_URL at build time for deployments;
// falls back to the local FastAPI dev server.
export const API_BASE = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

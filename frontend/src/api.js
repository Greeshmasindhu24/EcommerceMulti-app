import axios from 'axios';

/** Live frontend: https://ecommercemulti-app.onrender.com → API: https://ecommercemulti-app1.onrender.com */
const DEFAULT_RENDER_API = 'https://ecommercemulti-app1.onrender.com';

function isPrivateLanHost(hostname) {
  return (
    /^192\.168\.\d{1,3}\.\d{1,3}$/.test(hostname)
    || /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(hostname)
    || /^172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}$/.test(hostname)
  );
}

/** Pick API base URL for laptop, phone on Wi‑Fi, or live Render deployment. */
export function resolveApiUrl() {
  const envUrl = (process.env.REACT_APP_API_URL || '').trim().replace(/\/$/, '');
  const { protocol, hostname } = window.location;

  if (envUrl && !envUrl.includes('localhost') && !envUrl.includes('127.0.0.1')) {
    return envUrl;
  }

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return envUrl || 'http://localhost:5000';
  }

  if (isPrivateLanHost(hostname)) {
    return `${protocol}//${hostname}:5000`;
  }

  return DEFAULT_RENDER_API;
}

export const API_URL = resolveApiUrl();

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
});

function getStoredToken() {
  const raw = localStorage.getItem('token');
  if (!raw) return null;
  const token = raw.trim().replace(/^Bearer\s+/i, '');
  return token || null;
}

export function clearAuthStorage() {
  localStorage.removeItem('token');
  localStorage.removeItem('email');
  localStorage.removeItem('user');
}

export function saveAuthSession(accessToken, email) {
  clearAuthStorage();
  localStorage.setItem('token', accessToken.trim().replace(/^Bearer\s+/i, ''));
  if (email) {
    localStorage.setItem('email', email);
  }
}

api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isAuthRequest = error.config?.url?.includes('/login')
      || error.config?.url?.includes('/register')
      || error.config?.url?.includes('/chat');
    if (error.response?.status === 401 && !isAuthRequest) {
      clearAuthStorage();
      if (!window.location.pathname.includes('/auth')) {
        window.location.href = '/auth';
      }
    }
    return Promise.reject(error);
  }
);

export const loginUser = async (email, password) => {
  const response = await api.post('/login', { email, password });
  return response.data;
};

export const registerUser = async (email, password) => {
  const response = await api.post('/register', { email, password });
  return response.data;
};

export const verifyAuth = async () => {
  const response = await api.get('/auth/verify');
  return response.data;
};

export const getProducts = async (category = 'all') => {
  const response = await api.get(`/products/${category}`);
  return response.data;
};

export const placeOrder = async (orderData) => {
  const response = await api.post('/orders', orderData);
  return response.data;
};

export const getOrders = async () => {
  const response = await api.get('/orders');
  return response.data;
};

export const sendChatMessage = async (message, lastSeenProducts = []) => {
  const response = await api.post('/chat', { message, last_seen_products: lastSeenProducts });
  return response.data;
};

export default api;

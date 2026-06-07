import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
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

export const sendChatMessage = async (message) => {
  const response = await api.post('/chat', { message });
  return response.data;
};

export default api;

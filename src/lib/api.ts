import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';
import { useAuthStore } from '../stores/authStore';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:3000/api';

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach access token to every request
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

// Token refresh interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (isRefreshing) {
      return new Promise((resolve) => {
        refreshQueue.push((newToken: string) => {
          original.headers.Authorization = `Bearer ${newToken}`;
          resolve(api(original));
        });
      });
    }

    isRefreshing = true;

    try {
      const refreshToken = useAuthStore.getState().refreshToken;
      const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refreshToken });
      const { accessToken } = data;

      useAuthStore.getState().setTokens(accessToken, refreshToken!);
      refreshQueue.forEach((cb) => cb(accessToken));
      refreshQueue = [];

      original.headers.Authorization = `Bearer ${accessToken}`;
      return api(original);
    } catch {
      useAuthStore.getState().logout();
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
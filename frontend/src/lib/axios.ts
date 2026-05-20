import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL:         API_URL,
  headers:         { "Content-Type": "application/json" },
  timeout:         15000,
  withCredentials: true,   // httpOnly cookie uchun muhim
});

// Request interceptor — access token qo'shish (memory dan)
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor — 401 da refresh
let _refreshing = false;
let _waitQueue:  Array<(token: string) => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    // Bir vaqtda bir nechta so'rov bo'lsa — birinchisi refresh qiladi, qolganlari kutadi
    if (_refreshing) {
      return new Promise((resolve) => {
        _waitQueue.push((token: string) => {
          original.headers.Authorization = `Bearer ${token}`;
          resolve(api(original));
        });
      });
    }

    original._retry = true;
    _refreshing     = true;

    try {
      // refresh_token httpOnly cookie dan avtomatik yuboriladi (withCredentials: true)
      const { data } = await axios.post(
        `${API_URL}/auth/token/refresh/`,
        {},
        { withCredentials: true }
      );

      const newAccess = data.access;
      localStorage.setItem("access_token", newAccess);

      // Zustand store ni yangilaymiz
      const { useAuthStore } = await import("@/store/authStore");
      useAuthStore.getState().setToken(newAccess);

      original.headers.Authorization = `Bearer ${newAccess}`;

      // Kutayotgan so'rovlarni ozod qilamiz
      _waitQueue.forEach((cb) => cb(newAccess));
      _waitQueue = [];

      return api(original);
    } catch {
      // Refresh ham muvaffaqiyatsiz — logout
      const { useAuthStore } = await import("@/store/authStore");
      useAuthStore.getState().logout();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    } finally {
      _refreshing = false;
    }
  }
);

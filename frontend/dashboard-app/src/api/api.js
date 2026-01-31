import axios from "axios";

// In dev, Vite proxies /api to backend; baseURL stays relative so it works with proxy
const baseURL = import.meta.env.DEV ? "/api" : "http://localhost:5000/api";

const api = axios.create({ baseURL });

// Optional: attach auth token from localStorage when available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;

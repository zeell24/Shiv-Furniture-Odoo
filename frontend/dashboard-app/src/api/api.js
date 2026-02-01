import axios from "axios";

// In dev, Vite proxies /api to backend; baseURL stays relative so it works with proxy
const baseURL = import.meta.env.DEV ? "/api" : "http://localhost:5000/api";

const api = axios.create({ baseURL });

// Attach auth token from localStorage when available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401/422 (invalid or expired token), clear session and reload so user is sent to login page
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response?.status;
    const url = err.config?.url ?? "";
    const isAuthEndpoint = url.includes("/auth/demo") || url.includes("/auth/login");
    if ((status === 401 || status === 422) && !isAuthEndpoint) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.dispatchEvent(new CustomEvent("auth:sessionExpired"));
      window.location.reload();
    }
    return Promise.reject(err);
  }
);

export default api;

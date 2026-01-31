import { createContext, useState, useEffect } from "react";
import api from "../api/api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const u = localStorage.getItem("user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token && user) {
      setLoading(false);
      return;
    }
    if (!token) {
      api
        .post("/auth/demo")
        .then((res) => {
          const { access_token, user: u } = res.data;
          localStorage.setItem("token", access_token);
          localStorage.setItem("user", JSON.stringify(u));
          setUser(u);
        })
        .catch(() => {
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (email, password) => {
    return api.post("/auth/login", { email, password }).then((res) => {
      const { access_token, user: u } = res.data;
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(u));
      setUser(u);
      return u;
    });
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

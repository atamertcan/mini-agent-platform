import { useState, useEffect } from "react";
import { api, setUnauthorizedHandler } from "./api";
import AuthView from "./AuthView";
import DashboardView from "./DashboardView";
import "./App.css";

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    api.me(token).then(setUser).catch(handleLogout);
  }, [token]);

  useEffect(() => {
    setUnauthorizedHandler(handleLogout);
  });

  function handleLogin(newToken) {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  if (!token || !user) {
    return <AuthView onLogin={handleLogin} />;
  }

  return <DashboardView token={token} user={user} onLogout={handleLogout} />;
}

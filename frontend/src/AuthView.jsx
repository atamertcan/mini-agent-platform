import { useState } from "react";
import { api } from "./api";

export default function AuthView({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setInfo("");
    setLoading(true);
    try {
      if (mode === "register") {
        await api.register({ email, password, tenant_name: tenantName });
        setMode("login");
        setInfo("Kayıt başarılı, şimdi giriş yapabilirsin.");
      } else {
        const data = await api.login({ email, password });
        onLogin(data.access_token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <h1>Mini Agent Platform</h1>

      <div className="tabs">
        <button
          className={mode === "login" ? "active" : ""}
          onClick={() => { setMode("login"); setError(""); setInfo(""); }}
        >
          Giriş Yap
        </button>
        <button
          className={mode === "register" ? "active" : ""}
          onClick={() => { setMode("register"); setError(""); setInfo(""); }}
        >
          Kayıt Ol
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Şifre
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {mode === "register" && (
          <label>
            Şirket / Tenant Adı
            <input type="text" value={tenantName} onChange={(e) => setTenantName(e.target.value)} required />
          </label>
        )}

        {error && <p className="error">{error}</p>}
        {info && <p className="info">{info}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "..." : mode === "login" ? "Giriş Yap" : "Kayıt Ol"}
        </button>
      </form>
    </div>
  );
}

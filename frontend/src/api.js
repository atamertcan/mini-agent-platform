const API_BASE = "http://localhost:8000";

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let message = res.statusText;
    try {
      const data = await res.json();
      message = data.detail || message;
    } catch {
      // gövde yoksa/JSON değilse, res.statusText ile devam et
    }
    throw new Error(message);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  register: (data) => request("/auth/register", { method: "POST", body: data }),
  login: (data) => request("/auth/login", { method: "POST", body: data }),
  me: (token) => request("/auth/me", { token }),
  listAgents: (token) => request("/agents/", { token }),
  createAgent: (data, token) => request("/agents/", { method: "POST", body: data, token }),
  updateAgent: (id, data, token) => request(`/agents/${id}`, { method: "PATCH", body: data, token }),
  deleteAgent: (id, token) => request(`/agents/${id}`, { method: "DELETE", token }),
};

import { useState, useEffect } from "react";
import { api } from "./api";
import ToolsView from "./ToolsView";
import ChatView from "./ChatView";

const DEFAULT_MODEL = "anthropic/claude-haiku-4.5";
const emptyForm = { name: "", system_prompt: "", model: "", temperature: 0.7 };

export default function DashboardView({ token, user, onLogout }) {
  const [agents, setAgents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [managingToolsFor, setManagingToolsFor] = useState(null);
  const [chattingWith, setChattingWith] = useState(null);

  useEffect(() => {
    loadAgents();
  }, []);

  async function loadAgents() {
    setLoading(true);
    try {
      setAgents(await api.listAgents(token));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    const payload = { ...form, model: form.model.trim() || DEFAULT_MODEL };
    try {
      if (editingId) {
        await api.updateAgent(editingId, payload, token);
      } else {
        await api.createAgent(payload, token);
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadAgents();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(agent) {
    setEditingId(agent.id);
    setForm({
      name: agent.name,
      system_prompt: agent.system_prompt,
      model: agent.model,
      temperature: agent.temperature,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleDelete(id) {
    if (!window.confirm("Bu agent'i silmek istediğine emin misin?")) return;
    setError("");
    try {
      await api.deleteAgent(id, token);
      await loadAgents();
    } catch (err) {
      setError(err.message);
    }
  }

  if (managingToolsFor) {
    return (
      <ToolsView agent={managingToolsFor} token={token} onBack={() => setManagingToolsFor(null)} />
    );
  }

  if (chattingWith) {
    return <ChatView agent={chattingWith} token={token} onBack={() => setChattingWith(null)} />;
  }

  return (
    <div className="dashboard">
      <header>
        <h1>Mini Agent Platform</h1>
        <div className="user-bar">
          <span>{user.email}</span>
          <button onClick={onLogout}>Çıkış Yap</button>
        </div>
      </header>

      <section className="agent-form">
        <h2>{editingId ? "Agent Güncelle" : "Yeni Agent"}</h2>
        <form onSubmit={handleSubmit}>
          <label>
            İsim
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>
          <label>
            System Prompt
            <textarea
              value={form.system_prompt}
              onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
              rows={3}
            />
          </label>
          <label>
            Model
            <input
              value={form.model}
              onChange={(e) => setForm({ ...form, model: e.target.value })}
              placeholder={DEFAULT_MODEL}
            />
          </label>
          <label>
            Temperature
            <input
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={form.temperature}
              onChange={(e) => setForm({ ...form, temperature: parseFloat(e.target.value) })}
            />
          </label>

          {error && <p className="error">{error}</p>}

          <div className="form-actions">
            <button type="submit">{editingId ? "Güncelle" : "Oluştur"}</button>
            {editingId && (
              <button type="button" onClick={cancelEdit}>
                İptal
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="agent-list">
        <h2>Agentlarım ({agents.length})</h2>
        {loading ? (
          <p>Yükleniyor...</p>
        ) : agents.length === 0 ? (
          <p>Henüz agent yok.</p>
        ) : (
          <ul>
            {agents.map((agent) => (
              <li key={agent.id}>
                <div className="item-info">
                  <strong>{agent.name}</strong>
                  <span className="meta">
                    {agent.model} · temp {agent.temperature}
                  </span>
                  {agent.system_prompt && <p className="prompt">{agent.system_prompt}</p>}
                </div>
                <div className="item-actions">
                  <button onClick={() => setChattingWith(agent)}>Sohbet</button>
                  <button onClick={() => setManagingToolsFor(agent)}>Toollar</button>
                  <button onClick={() => startEdit(agent)}>Düzenle</button>
                  <button onClick={() => handleDelete(agent.id)}>Sil</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

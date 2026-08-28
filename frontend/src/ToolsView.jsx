import { useState, useEffect } from "react";
import { api } from "./api";

const emptyParam = { name: "", type: "string", description: "", required: true };
const emptyHeader = { key: "", value: "" };
const emptyForm = { name: "", description: "", url: "", http_method: "POST", parameters: [], headers: [] };

function headersToDict(headers) {
  return Object.fromEntries(headers.filter((h) => h.key.trim()).map((h) => [h.key, h.value]));
}

function headersToRows(headers) {
  return Object.entries(headers || {}).map(([key, value]) => ({ key, value }));
}

export default function ToolsView({ agent, token, onBack }) {
  const [tools, setTools] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTools();
  }, []);

  async function loadTools() {
    setLoading(true);
    try {
      setTools(await api.listTools(agent.id, token));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    const payload = { ...form, headers: headersToDict(form.headers) };
    try {
      if (editingId) {
        await api.updateTool(agent.id, editingId, payload, token);
      } else {
        await api.createTool(agent.id, payload, token);
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadTools();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(tool) {
    setEditingId(tool.id);
    setForm({
      name: tool.name,
      description: tool.description,
      url: tool.url,
      http_method: tool.http_method,
      parameters: tool.parameters,
      headers: headersToRows(tool.headers),
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleDelete(toolId) {
    if (!window.confirm("Bu tool'u silmek istediğine emin misin?")) return;
    setError("");
    try {
      await api.deleteTool(agent.id, toolId, token);
      await loadTools();
    } catch (err) {
      setError(err.message);
    }
  }

  function addParam() {
    setForm({ ...form, parameters: [...form.parameters, { ...emptyParam }] });
  }

  function updateParam(index, field, value) {
    const updated = form.parameters.map((p, i) => (i === index ? { ...p, [field]: value } : p));
    setForm({ ...form, parameters: updated });
  }

  function removeParam(index) {
    setForm({ ...form, parameters: form.parameters.filter((_, i) => i !== index) });
  }

  function addHeader() {
    setForm({ ...form, headers: [...form.headers, { ...emptyHeader }] });
  }

  function updateHeader(index, field, value) {
    const updated = form.headers.map((h, i) => (i === index ? { ...h, [field]: value } : h));
    setForm({ ...form, headers: updated });
  }

  function removeHeader(index) {
    setForm({ ...form, headers: form.headers.filter((_, i) => i !== index) });
  }

  return (
    <div className="dashboard">
      <header>
        <h1>{agent.name} Toollar</h1>
        <button onClick={onBack}>Agentlara Dön</button>
      </header>

      <section className="agent-form">
        <h2>{editingId ? "Tool Güncelle" : "Yeni Tool"}</h2>
        <form onSubmit={handleSubmit}>
          <label>
            İsim
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label>
            Açıklama
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              required
            />
          </label>
          <label>
            URL
            <input
              value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder="https://wttr.in/{city}?format=3"
              required
            />
          </label>
          <label>
            HTTP Metodu
            <select value={form.http_method} onChange={(e) => setForm({ ...form, http_method: e.target.value })}>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </label>

          <div className="param-list">
            <div className="param-list-header">
              <span>Parametreler</span>
              <button type="button" onClick={addParam}>
                + Parametre Ekle
              </button>
            </div>
            {form.parameters.map((param, i) => (
              <div className="param-row" key={i}>
                <input
                  placeholder="isim"
                  value={param.name}
                  onChange={(e) => updateParam(i, "name", e.target.value)}
                />
                <select value={param.type} onChange={(e) => updateParam(i, "type", e.target.value)}>
                  <option value="string">string</option>
                  <option value="integer">integer</option>
                  <option value="number">number</option>
                  <option value="boolean">boolean</option>
                </select>
                <input
                  placeholder="açıklama"
                  value={param.description}
                  onChange={(e) => updateParam(i, "description", e.target.value)}
                />
                <label className="param-required">
                  <input
                    type="checkbox"
                    checked={param.required}
                    onChange={(e) => updateParam(i, "required", e.target.checked)}
                  />
                  zorunlu
                </label>
                <button type="button" onClick={() => removeParam(i)}>
                  Sil
                </button>
              </div>
            ))}
          </div>

          <div className="param-list">
            <div className="param-list-header">
              <span>Headerlar (API key / Authorization vb.)</span>
              <button type="button" onClick={addHeader}>
                + Header Ekle
              </button>
            </div>
            {form.headers.map((header, i) => (
              <div className="header-row" key={i}>
                <input
                  placeholder="Authorization"
                  value={header.key}
                  onChange={(e) => updateHeader(i, "key", e.target.value)}
                />
                <input
                  placeholder="Bearer xxxx"
                  value={header.value}
                  onChange={(e) => updateHeader(i, "value", e.target.value)}
                />
                <button type="button" onClick={() => removeHeader(i)}>
                  Sil
                </button>
              </div>
            ))}
          </div>

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
        <h2>Toollar ({tools.length})</h2>
        {loading ? (
          <p>Yükleniyor...</p>
        ) : tools.length === 0 ? (
          <p>Henüz tool yok.</p>
        ) : (
          <ul>
            {tools.map((tool) => (
              <li key={tool.id}>
                <div className="item-info">
                  <strong>{tool.name}</strong>
                  <span className="meta">
                    {tool.http_method} · {tool.url}
                  </span>
                  <p className="prompt">{tool.description}</p>
                  {tool.parameters.length > 0 && (
                    <p className="meta">
                      Parametreler: {tool.parameters.map((p) => `${p.name}${p.required ? "*" : ""}`).join(", ")}
                    </p>
                  )}
                  {Object.keys(tool.headers || {}).length > 0 && (
                    <p className="meta">Headerlar: {Object.keys(tool.headers).join(", ")}</p>
                  )}
                </div>
                <div className="item-actions">
                  <button onClick={() => startEdit(tool)}>Düzenle</button>
                  <button onClick={() => handleDelete(tool.id)}>Sil</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

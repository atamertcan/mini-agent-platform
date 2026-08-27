import { useState, useRef, useEffect } from "react";
import { api } from "./api";

export default function ChatView({ agent, token, onBack }) {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function handleSend(e) {
    e.preventDefault();
    const content = input.trim();
    if (!content || sending) return;

    setError("");
    setInput("");
    setMessages((prev) => [...prev, { id: `local-${Date.now()}`, role: "user", content }]);
    setSending(true);
    try {
      const response = await api.sendMessage(
        agent.id,
        { content, conversation_id: conversationId },
        token
      );
      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="dashboard">
      <header>
        <h1>{agent.name} — Sohbet</h1>
        <button onClick={onBack}>Agent'lara Dön</button>
      </header>

      <section className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && <p className="meta">Henüz mesaj yok, aşağıdan yazmaya başla.</p>}
          {messages.map((msg) => (
            <div key={msg.id} className={`chat-message ${msg.role}`}>
              <span className="chat-role">{msg.role === "user" ? "Sen" : "Agent"}</span>
              <p>{msg.content}</p>
            </div>
          ))}
          {sending && (
            <div className="chat-message assistant">
              <span className="chat-role">Agent</span>
              <p className="meta">yazıyor...</p>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && <p className="error">{error}</p>}

        <form className="chat-input-bar" onSubmit={handleSend}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Mesajını yaz..."
            disabled={sending}
          />
          <button type="submit" disabled={sending || !input.trim()}>
            Gönder
          </button>
        </form>
      </section>
    </div>
  );
}

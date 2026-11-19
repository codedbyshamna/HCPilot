import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import { api } from "../api";

const SUGGESTIONS = [
  "Show all interactions",
  "Summarize my last meeting",
  "Recommend a follow-up for my latest HCP",
  "Log a call with Dr. Meena Iyer today. She was positive about GlucoSafe.",
];

export default function ChatPanel({ onDataChanged }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, sending]);

  const send = async (text) => {
    const message = text.trim();
    if (!message || sending) return;

    // Only real conversation turns go back to the AI as context, not error notes.
    const history = messages.filter((m) => m.role !== "error");
    setMessages([...messages, { role: "user", content: message }]);
    setInput("");
    setSending(true);
    try {
      const data = await api.chat(message, history);
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      if (data.data_changed) onDataChanged();
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", content: err.message }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <section className="panel chat">
      <div className="panel-head">
        <h2>AI assistant</h2>
        {messages.length > 0 && (
          <button className="secondary small" onClick={() => setMessages([])} disabled={sending}>
            New chat
          </button>
        )}
      </div>

      <div className="messages" aria-live="polite">
        {messages.length === 0 && (
          <div className="empty">
            <p className="muted">
              Ask about saved meetings, log or edit one in plain words, or get a summary and
              follow-up advice.
            </p>
            <div className="chips">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip" onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.role === "assistant" ? <Markdown>{m.content}</Markdown> : m.content}
          </div>
        ))}
        {sending && <div className="bubble assistant typing">Thinking…</div>}
        <div ref={endRef} />
      </div>

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the AI…"
          aria-label="Message the AI"
        />
        <button type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}

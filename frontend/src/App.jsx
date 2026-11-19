import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import ChatPanel from "./components/ChatPanel";
import InteractionForm from "./components/InteractionForm";
import InteractionList from "./components/InteractionList";
import ThemeToggle from "./components/ThemeToggle";
import "./App.css";

export default function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState("");
  const [editing, setEditing] = useState(null);
  const [notice, setNotice] = useState(null);

  const refresh = useCallback(async () => {
    try {
      setItems(await api.listInteractions());
      setListError("");
    } catch (err) {
      setListError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Loads data from the backend; refresh only sets state after the request finishes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(null), 4000);
    return () => clearTimeout(timer);
  }, [notice]);

  const handleSaved = (saved, wasEdit) => {
    setNotice({ type: "success", text: `${wasEdit ? "Updated" : "Saved"} interaction #${saved.id} with ${saved.hcp_name}.` });
    setEditing(null);
    refresh();
  };

  const handleDelete = async (item) => {
    if (!window.confirm(`Delete interaction #${item.id} with ${item.hcp_name}?`)) return;
    try {
      await api.deleteInteraction(item.id);
      if (editing?.id === item.id) setEditing(null);
      setNotice({ type: "success", text: `Deleted interaction #${item.id}.` });
      refresh();
    } catch (err) {
      setNotice({ type: "error", text: err.message });
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo" aria-hidden="true">+</span>
          <div>
            <h1>AI-First CRM</h1>
            <p className="muted">Healthcare professional interactions</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      {notice && (
        <div className={`notice ${notice.type}`} role="status">
          {notice.text}
        </div>
      )}

      <main className="grid">
        <InteractionForm
          key={editing?.id ?? "new"}
          editing={editing}
          onSaved={handleSaved}
          onCancel={() => setEditing(null)}
        />
        <ChatPanel onDataChanged={refresh} />
        <InteractionList
          items={items}
          loading={loading}
          error={listError}
          editingId={editing?.id}
          onEdit={(item) => {
            setEditing(item);
            window.scrollTo({ top: 0, behavior: "smooth" });
          }}
          onDelete={handleDelete}
        />
      </main>
    </div>
  );
}

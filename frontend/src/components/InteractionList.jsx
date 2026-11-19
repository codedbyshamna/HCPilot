import { useState } from "react";

function formatWhen(item) {
  if (!item.interaction_date) return "No date";
  const date = new Date(item.interaction_date + "T00:00").toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
  return item.interaction_time ? `${date}, ${item.interaction_time.slice(0, 5)}` : date;
}

const DETAILS = [
  ["attendees", "Attendees"],
  ["topics_discussed", "Topics"],
  ["materials_shared", "Materials"],
  ["samples_distributed", "Samples"],
  ["outcomes", "Outcome"],
  ["follow_up_actions", "Follow-up"],
];

export default function InteractionList({ items, loading, error, editingId, onEdit, onDelete }) {
  const [search, setSearch] = useState("");
  const query = search.trim().toLowerCase();
  const shown = query ? items.filter((i) => i.hcp_name.toLowerCase().includes(query)) : items;

  return (
    <section className="panel list">
      <div className="panel-head">
        <h2>
          Saved interactions <span className="count">{items.length}</span>
        </h2>
        <input
          className="search"
          type="search"
          placeholder="Search by HCP name"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && <p className="error">{error}</p>}
      {loading && !items.length && <p className="muted">Loading…</p>}
      {!loading && !error && !items.length && (
        <p className="muted">No interactions yet. Log one with the form or ask the AI.</p>
      )}
      {query && items.length > 0 && !shown.length && <p className="muted">No HCP matches “{search}”.</p>}

      <div className="cards">
        {shown.map((item) => (
          <article key={item.id} className={`card ${item.id === editingId ? "editing" : ""}`}>
            <header>
              <div>
                <h3>{item.hcp_name}</h3>
                <p className="muted">
                  #{item.id} · {item.interaction_type || "Interaction"} · {formatWhen(item)}
                </p>
              </div>
              {item.sentiment && (
                <span className={`badge ${item.sentiment.toLowerCase()}`}>{item.sentiment}</span>
              )}
            </header>
            <dl>
              {DETAILS.filter(([key]) => item[key]).map(([key, label]) => (
                <div key={key}>
                  <dt>{label}</dt>
                  <dd>{item[key]}</dd>
                </div>
              ))}
            </dl>
            <footer>
              <button className="secondary small" onClick={() => onEdit(item)}>
                Edit
              </button>
              <button className="danger small" onClick={() => onDelete(item)}>
                Delete
              </button>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}

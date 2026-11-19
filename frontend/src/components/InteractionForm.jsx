import { useState } from "react";
import { api } from "../api";

const INTERACTION_TYPES = ["Meeting", "Call", "Email", "Conference", "Other"];
const SENTIMENTS = ["Positive", "Neutral", "Negative"];

function today() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function emptyForm() {
  return {
    hcp_name: "",
    interaction_type: "Meeting",
    interaction_date: today(),
    interaction_time: "",
    attendees: "",
    topics_discussed: "",
    materials_shared: "",
    samples_distributed: "",
    sentiment: "",
    outcomes: "",
    follow_up_actions: "",
  };
}

function formFrom(interaction) {
  const form = emptyForm();
  for (const key of Object.keys(form)) {
    form[key] = interaction[key] ?? "";
  }
  form.interaction_time = form.interaction_time.slice(0, 5); // "10:30:00" -> "10:30"
  return form;
}

export default function InteractionForm({ editing, onSaved, onCancel }) {
  const [form, setForm] = useState(() => (editing ? formFrom(editing) : emptyForm()));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (!form.hcp_name.trim()) {
      setError("HCP name is required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const saved = editing
        ? await api.updateInteraction(editing.id, form)
        : await api.createInteraction(form);
      if (!editing) setForm(emptyForm());
      onSaved(saved, Boolean(editing));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="panel form" onSubmit={submit} noValidate>
      <div className="panel-head">
        <h2>{editing ? `Edit interaction #${editing.id}` : "Log interaction"}</h2>
      </div>

      <label className="field span-2">
        <span>
          HCP name <em>*</em>
        </span>
        <input
          name="hcp_name"
          value={form.hcp_name}
          onChange={set}
          placeholder="e.g. Dr. Rajesh Kumar"
          required
        />
      </label>

      <label className="field">
        <span>Interaction type</span>
        <select name="interaction_type" value={form.interaction_type} onChange={set}>
          <option value="">—</option>
          {INTERACTION_TYPES.map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Sentiment</span>
        <select name="sentiment" value={form.sentiment} onChange={set}>
          <option value="">—</option>
          {SENTIMENTS.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Date</span>
        <input type="date" name="interaction_date" value={form.interaction_date} onChange={set} />
      </label>

      <label className="field">
        <span>Time</span>
        <input type="time" name="interaction_time" value={form.interaction_time} onChange={set} />
      </label>

      <label className="field span-2">
        <span>Attendees</span>
        <input name="attendees" value={form.attendees} onChange={set} placeholder="e.g. Dr. Kumar, Nurse Priya" />
      </label>

      <label className="field span-2">
        <span>Topics discussed</span>
        <textarea name="topics_discussed" rows={2} value={form.topics_discussed} onChange={set} />
      </label>

      <label className="field">
        <span>Materials shared</span>
        <input name="materials_shared" value={form.materials_shared} onChange={set} placeholder="e.g. Product brochure" />
      </label>

      <label className="field">
        <span>Samples distributed</span>
        <input name="samples_distributed" value={form.samples_distributed} onChange={set} placeholder="e.g. 10 strips" />
      </label>

      <label className="field span-2">
        <span>Outcome</span>
        <textarea name="outcomes" rows={2} value={form.outcomes} onChange={set} />
      </label>

      <label className="field span-2">
        <span>Follow-up actions</span>
        <textarea name="follow_up_actions" rows={2} value={form.follow_up_actions} onChange={set} />
      </label>

      {error && <p className="error span-2">{error}</p>}

      <div className="actions span-2">
        {editing && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : editing ? "Save changes" : "Save interaction"}
        </button>
      </div>
    </form>
  );
}

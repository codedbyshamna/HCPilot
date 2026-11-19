const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const FIELD_NAMES = {
  hcp_name: "HCP name",
  interaction_date: "Date",
  interaction_time: "Time",
  message: "Message",
};

function errorMessage(body, status) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // FastAPI validation errors (422): list each field problem.
    return detail
      .map((e) => {
        const field = e.loc?.[e.loc.length - 1];
        return `${FIELD_NAMES[field] ?? field}: ${e.msg}`;
      })
      .join(". ");
  }
  return `Request failed (HTTP ${status})`;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(API_URL + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error(`Cannot reach the backend at ${API_URL}. Is it running?`);
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // Some responses have no JSON body.
  }
  if (!response.ok) throw new Error(errorMessage(body, response.status));
  return body;
}

export const api = {
  listInteractions: () => request("/interactions/"),
  createInteraction: (data) =>
    request("/interactions/", { method: "POST", body: JSON.stringify(data) }),
  updateInteraction: (id, data) =>
    request(`/interactions/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteInteraction: (id) => request(`/interactions/${id}`, { method: "DELETE" }),
  chat: (message, history) =>
    request("/ai/chat", { method: "POST", body: JSON.stringify({ message, history }) }),
};

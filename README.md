# AI-First CRM – HCP Interaction Module

An AI-powered CRM for pharmaceutical field representatives to record their interactions with Healthcare Professionals (HCPs). Interactions can be logged through a form or by chatting with an AI assistant built with LangGraph and a free Groq-hosted LLM. The assistant reads and writes the same database as the form.

---

## 🚀 Features

- 📝 Log HCP interactions with a structured form (type, date, time, attendees, topics, materials, samples, sentiment, outcome, follow-up)
- 📋 View, search, edit and delete saved interactions
- 🤖 AI assistant that works on the real data:
  - log a new interaction from a plain-language description
  - edit an existing interaction
  - answer questions about past interactions
  - summarize interactions
  - recommend follow-up actions based on an HCP's history
- 💬 The chat remembers earlier messages in the conversation
- ⚡ FastAPI REST API with Swagger docs

---

## 🛠 Tech Stack

**Frontend:** React 19, Vite, plain CSS (light and dark mode)

**Backend:** Python 3.11+, FastAPI, SQLAlchemy, LangGraph, LangChain, Groq (`openai/gpt-oss-120b` by default, free tier)

**Database:** PostgreSQL, or SQLite with no setup (used automatically when `DATABASE_URL` is not set)

---

## 📁 Project Structure

```
aivoa-ai-crm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router registration
│   │   ├── config.py            # settings read from .env
│   │   ├── database.py          # SQLAlchemy engine and session
│   │   ├── models/              # Interaction table
│   │   ├── schemas/             # request/response validation
│   │   ├── services/            # database operations (shared by API and AI tools)
│   │   ├── routers/
│   │   │   ├── interaction.py   # /interactions CRUD endpoints
│   │   │   └── ai.py            # /ai/chat endpoint
│   │   └── langgraph/
│   │       ├── llm.py           # Groq model setup
│   │       ├── agent.py         # LangGraph ReAct agent + system prompt
│   │       └── tools.py         # the five CRM tools
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api.js               # backend calls and error handling
│       └── components/          # InteractionForm, InteractionList, ChatPanel
└── README.md
```

---

## 🤖 LangGraph AI Agent

The `/ai/chat` endpoint runs a LangGraph ReAct agent. The LLM reads the user's message, decides which tool to call, reads the tool's result, and replies. It is told today's date so phrases like "yesterday" or "next Monday" become real dates, and it is instructed to answer only from tool results.

| Tool | What it does | Example prompt |
|---|---|---|
| `log_interaction` | Saves a new interaction to the database | "Log a meeting with Dr. Rajesh Kumar today. We discussed CardioPlus and he was positive." |
| `edit_interaction` | Updates fields of an existing interaction by id | "Change the follow-up for Dr. Kumar's last meeting to next Monday." |
| `get_interactions` | Looks up saved interactions, optionally by HCP name | "What meetings did I have with Dr. Meena Iyer?" |
| `summarize_interactions` | Summarizes one interaction or all visits with an HCP | "Summarize my visits with Dr. Kumar." |
| `recommend_followup` | Suggests next steps based on an HCP's history | "Recommend a follow-up for Dr. Kumar." |

---

## ⚙️ Setup

### 1. Get a free Groq API key

Sign up at https://console.groq.com/keys and create a key. The free tier is enough for this app.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
copy .env.example .env         # Windows  (cp on macOS / Linux)
```

Edit `backend/.env` and set `GROQ_API_KEY`.

**Database:**
- **SQLite (easiest):** leave `DATABASE_URL` unset. A file `backend/aivoa_crm.db` is created automatically.
- **PostgreSQL:** start one with Docker and set `DATABASE_URL`:
  ```bash
  docker run -d --name aivoa-postgres -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=aivoa_crm -p 5432:5432 postgres:16
  ```
  ```
  DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/aivoa_crm
  ```

Run the backend:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

The form and saved-interactions list work without a Groq key. Only the AI chat needs it.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

To use a backend on a different address, set `VITE_API_URL` (for example in `frontend/.env`).

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/interactions/?hcp_name=` | List interactions, newest first (optional name filter) |
| GET | `/interactions/{id}` | Get one interaction |
| POST | `/interactions/` | Create an interaction (`hcp_name` required) |
| PUT | `/interactions/{id}` | Update an interaction (only the fields sent are changed) |
| DELETE | `/interactions/{id}` | Delete an interaction |
| POST | `/ai/chat` | Chat with the AI assistant |

### `POST /ai/chat`

Request:

```json
{
  "message": "Summarize my visits with Dr. Kumar",
  "history": [
    { "role": "user", "content": "Show all interactions" },
    { "role": "assistant", "content": "You have 2 interactions..." }
  ]
}
```

Response:

```json
{
  "response": "You met Dr. Rajesh Kumar on 19 Nov 2026 to discuss CardioPlus...",
  "data_changed": false
}
```

`data_changed` is `true` when the AI saved or edited an interaction. The frontend uses it to refresh the list.

---

## 🔮 Future Enhancements

- User authentication and role-based access
- Database migrations (Alembic)
- AI analytics dashboard
- Voice-to-text interaction logging
- Email and calendar integration

---

## Author

**Shamna**

GitHub: https://github.com/codedbyshamna

Project Repository: https://github.com/codedbyshamna/aivoa-ai-crm

---

## Assignment Information

This project was developed as part of the **AIVOA AI-First CRM HCP Interaction Module Technical Assignment**.

The solution demonstrates:
- React frontend
- FastAPI backend
- LangGraph AI agent
- Groq LLM integration
- AI-assisted CRM workflow
- Five LangGraph tools for HCP interaction management, connected to the database

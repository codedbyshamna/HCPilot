"""Central place for settings. Values come from backend/.env (see .env.example)."""
import os

from dotenv import load_dotenv

load_dotenv()

# Falls back to a local SQLite file so the app runs even without PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aivoa_crm.db")

# Groq offers a free tier: create a key at https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

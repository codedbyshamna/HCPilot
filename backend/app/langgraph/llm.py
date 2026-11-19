from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY, GROQ_MODEL


class MissingAPIKeyError(RuntimeError):
    pass


@lru_cache
def get_llm() -> ChatGroq:
    """Created on first use so the server can start (and the form works) without a key."""
    if not GROQ_API_KEY:
        raise MissingAPIKeyError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
            "and add it to backend/.env, then restart the backend."
        )
    return ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0)

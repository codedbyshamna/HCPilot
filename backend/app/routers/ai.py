import logging
from typing import Literal

import groq
from fastapi import APIRouter, HTTPException
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field

from app.langgraph.agent import get_agent
from app.langgraph.llm import MissingAPIKeyError
from app.langgraph.tools import WRITE_TOOLS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])

MAX_HISTORY = 20


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    # Earlier turns of the conversation, so the AI remembers context.
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    data_changed: bool  # True when the AI saved or edited an interaction


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages = [m.model_dump() for m in request.history[-MAX_HISTORY:]]
    messages.append({"role": "user", "content": request.message})

    try:
        result = get_agent().invoke({"messages": messages})
    except MissingAPIKeyError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except groq.AuthenticationError:
        raise HTTPException(
            status_code=503,
            detail="The Groq API key was rejected. Check GROQ_API_KEY in backend/.env.",
        )
    except groq.RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="The free Groq limit was reached. Wait a minute and try again.",
        )
    except groq.BadRequestError:
        logger.exception("Groq rejected the request")
        raise HTTPException(
            status_code=502,
            detail="The AI could not process that request. Try rephrasing it.",
        )
    except groq.APIError:
        logger.exception("Groq API error")
        raise HTTPException(status_code=502, detail="The AI service is unavailable right now.")

    data_changed = any(
        isinstance(m, ToolMessage) and m.name in WRITE_TOOLS for m in result["messages"]
    )
    return ChatResponse(response=result["messages"][-1].content, data_changed=data_changed)

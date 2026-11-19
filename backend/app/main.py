from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.models.interaction import Interaction  # noqa: F401  (registers the table)
from app.routers.ai import router as ai_router
from app.routers.interaction import router as interaction_router

app = FastAPI(title="AIVOA AI CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(interaction_router)
app.include_router(ai_router)


@app.get("/")
def home():
    return {"message": "AIVOA AI CRM Backend Running"}


@app.get("/health")
def health():
    return {"status": "Connected"}

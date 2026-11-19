from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionUpdate,
)
from app.services import interactions as service

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"],
)


def _get_or_404(db: Session, interaction_id: int):
    interaction = service.get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.post("/", response_model=InteractionResponse, status_code=201)
def create_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    return service.create_interaction(db, interaction)


@router.get("/", response_model=list[InteractionResponse])
def list_interactions(hcp_name: Optional[str] = None, db: Session = Depends(get_db)):
    return service.list_interactions(db, hcp_name=hcp_name)


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, interaction_id)


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    interaction: InteractionUpdate,
    db: Session = Depends(get_db),
):
    db_interaction = _get_or_404(db, interaction_id)
    return service.update_interaction(db, db_interaction, interaction)


@router.delete("/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    db_interaction = _get_or_404(db, interaction_id)
    service.delete_interaction(db, db_interaction)
    return {"message": "Interaction deleted successfully"}

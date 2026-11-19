"""Database operations for interactions, shared by the REST API and the AI tools."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate


def create_interaction(db: Session, data: InteractionCreate) -> Interaction:
    interaction = Interaction(**data.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction(db: Session, interaction_id: int) -> Optional[Interaction]:
    return db.get(Interaction, interaction_id)


def list_interactions(
    db: Session,
    hcp_name: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[Interaction]:
    query = db.query(Interaction)
    if hcp_name:
        query = query.filter(Interaction.hcp_name.ilike(f"%{hcp_name.strip()}%"))
    # Newest first: latest visit date, then most recently created.
    query = query.order_by(
        Interaction.interaction_date.desc().nulls_last(),
        Interaction.interaction_time.desc().nulls_last(),
        Interaction.id.desc(),
    )
    if limit:
        query = query.limit(limit)
    return query.all()


def update_interaction(
    db: Session, interaction: Interaction, data: InteractionUpdate
) -> Interaction:
    # exclude_unset: fields the caller did not send are left unchanged.
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "hcp_name" and not value:
            continue  # never blank out the required name
        setattr(interaction, key, value)
    db.commit()
    db.refresh(interaction)
    return interaction


def delete_interaction(db: Session, interaction: Interaction) -> None:
    db.delete(interaction)
    db.commit()

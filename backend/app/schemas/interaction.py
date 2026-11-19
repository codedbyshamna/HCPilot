from datetime import date, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class InteractionBase(BaseModel):
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None

    @field_validator("*", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        """The form sends "" for untouched fields; treat those as empty, not invalid."""
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class InteractionCreate(InteractionBase):
    # Blank names become None in blank_to_none, so they are rejected here.
    hcp_name: str


class InteractionUpdate(InteractionBase):
    """Every field is optional: only the fields sent are changed."""

    hcp_name: Optional[str] = None


class InteractionResponse(InteractionBase):
    id: int
    hcp_name: str

    model_config = ConfigDict(from_attributes=True)

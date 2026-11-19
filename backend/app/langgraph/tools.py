"""LangGraph tools the AI agent can call. Each one works on the real interactions table."""
from datetime import date
from typing import Optional

from langchain_core.tools import tool
from pydantic import ValidationError

from app.database import SessionLocal
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.services import interactions as service

FIELD_LABELS = {
    "interaction_type": "Type",
    "interaction_date": "Date",
    "interaction_time": "Time",
    "attendees": "Attendees",
    "topics_discussed": "Topics discussed",
    "materials_shared": "Materials shared",
    "samples_distributed": "Samples distributed",
    "sentiment": "Sentiment",
    "outcomes": "Outcomes",
    "follow_up_actions": "Follow-up actions",
}


def format_interaction(interaction: Interaction) -> str:
    lines = [f"Interaction #{interaction.id} with {interaction.hcp_name}"]
    for field, label in FIELD_LABELS.items():
        value = getattr(interaction, field)
        if value is not None and value != "":
            if field == "interaction_time":
                value = value.strftime("%H:%M")
            lines.append(f"  {label}: {value}")
    return "\n".join(lines)


def _validation_message(error: ValidationError) -> str:
    problems = "; ".join(
        f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in error.errors()
    )
    return (
        f"Could not save because some values are invalid ({problems}). "
        "Dates must be YYYY-MM-DD and times HH:MM (24-hour)."
    )


def _find_interactions(db, interaction_id: Optional[int], hcp_name: Optional[str], limit: int):
    if interaction_id:
        found = service.get_interaction(db, interaction_id)
        return [found] if found else []
    return service.list_interactions(db, hcp_name=hcp_name, limit=limit)


@tool
def log_interaction(
    hcp_name: str,
    interaction_type: Optional[str] = None,
    interaction_date: Optional[str] = None,
    interaction_time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[str] = None,
    samples_distributed: Optional[str] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
) -> str:
    """Save a NEW interaction with a healthcare professional (HCP) to the CRM database.

    Use only when the user describes a meeting/call that should be recorded.
    hcp_name is required (e.g. "Dr. Rajesh Kumar"). interaction_type is one of
    Meeting, Call, Email, Conference, Other. interaction_date is YYYY-MM-DD
    (defaults to today), interaction_time is HH:MM 24-hour. sentiment is
    Positive, Neutral or Negative. Leave out anything the user did not mention.
    """
    values = {k: v for k, v in locals().items() if v is not None}
    values.setdefault("interaction_date", date.today().isoformat())
    try:
        data = InteractionCreate(**values)
    except ValidationError as error:
        return _validation_message(error)

    with SessionLocal() as db:
        saved = service.create_interaction(db, data)
        return "Saved to the CRM.\n" + format_interaction(saved)


@tool
def edit_interaction(
    interaction_id: int,
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    interaction_date: Optional[str] = None,
    interaction_time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[str] = None,
    samples_distributed: Optional[str] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
) -> str:
    """Change fields of an EXISTING interaction, identified by its numeric interaction_id.

    Pass only the fields that should change; everything else stays as it is.
    If you do not know the id, call get_interactions first to find it.
    Dates are YYYY-MM-DD, times HH:MM 24-hour.
    """
    changes = {
        k: v for k, v in locals().items() if k != "interaction_id" and v is not None
    }
    if not changes:
        return "Nothing to change: no new field values were given."
    try:
        data = InteractionUpdate(**changes)
    except ValidationError as error:
        return _validation_message(error)

    with SessionLocal() as db:
        existing = service.get_interaction(db, interaction_id)
        if not existing:
            return f"No interaction with id {interaction_id} exists."
        updated = service.update_interaction(db, existing, data)
        return "Updated.\n" + format_interaction(updated)


@tool
def get_interactions(hcp_name: Optional[str] = None, limit: int = 20) -> str:
    """Look up saved interactions from the CRM database, newest first.

    Optionally filter by hcp_name (partial match, e.g. "Kumar"). Use this to
    answer questions about past meetings or to find an interaction's id.
    """
    with SessionLocal() as db:
        found = service.list_interactions(db, hcp_name=hcp_name, limit=limit)
        if not found:
            who = f" for '{hcp_name}'" if hcp_name else ""
            return f"No interactions found{who}."
        return f"{len(found)} interaction(s):\n\n" + "\n\n".join(
            format_interaction(i) for i in found
        )


@tool
def summarize_interactions(
    interaction_id: Optional[int] = None,
    hcp_name: Optional[str] = None,
) -> str:
    """Fetch the records needed to summarize saved interactions.

    Give interaction_id for one specific interaction, or hcp_name to summarize
    all visits with that HCP. With neither, the 5 most recent interactions are used.
    """
    with SessionLocal() as db:
        found = _find_interactions(db, interaction_id, hcp_name, limit=10 if hcp_name else 5)
        if not found:
            return "No matching interactions found, so there is nothing to summarize."
        records = "\n\n".join(format_interaction(i) for i in found)

    # The agent writes the summary itself from these records, so it ends up in the reply.
    return (
        "INSTRUCTIONS: Write the summary yourself in your reply to the user (they cannot "
        "see this tool output). In a few clear sentences cover who was met and when, what "
        "was discussed, materials/samples given, how the HCP responded and agreed next "
        "steps. Use only facts from these records.\n\nRECORDS:\n\n" + records
    )


@tool
def recommend_followup(
    interaction_id: Optional[int] = None,
    hcp_name: Optional[str] = None,
) -> str:
    """Fetch an HCP's interaction history to recommend next follow-up actions.

    Give hcp_name (preferred) or the interaction_id of a specific visit.
    """
    with SessionLocal() as db:
        if interaction_id and not hcp_name:
            single = service.get_interaction(db, interaction_id)
            hcp_name = single.hcp_name if single else None
            if not single:
                return f"No interaction with id {interaction_id} exists."
        found = service.list_interactions(db, hcp_name=hcp_name, limit=10)
        if not found:
            return "No matching interactions found, so no follow-up can be recommended."
        records = "\n\n".join(format_interaction(i) for i in found)

    return (
        "INSTRUCTIONS: Write the recommendations yourself in your reply to the user (they "
        f"cannot see this tool output). Today is {date.today().isoformat()}. Based only on "
        "the history below (newest first), give 2-4 concrete follow-up actions as a bullet "
        "list, each with a suggested date, then one sentence explaining why. Respect any "
        "follow-up the HCP already agreed to.\n\nHISTORY:\n\n" + records
    )


TOOLS = [
    log_interaction,
    edit_interaction,
    get_interactions,
    summarize_interactions,
    recommend_followup,
]

# Tools that change data; the frontend refreshes its list when one of these ran.
WRITE_TOOLS = {log_interaction.name, edit_interaction.name}

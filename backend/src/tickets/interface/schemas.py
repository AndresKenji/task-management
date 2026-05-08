from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from tickets.domain import Ticket, TicketStatus


class CreateTicketIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    reporter_id: UUID


class AssignTicketIn(BaseModel):
    assignee_id: UUID


class TicketOut(BaseModel):
    id: UUID
    title: str
    description: str
    reporter_id: UUID
    status: TicketStatus
    assignee_id: UUID | None
    created_at: datetime


def ticket_to_out(ticket: Ticket) -> TicketOut:
    return TicketOut(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        reporter_id=ticket.reporter_id,
        status=ticket.status,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
    )

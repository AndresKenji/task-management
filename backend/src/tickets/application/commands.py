from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class CreateTicketCommand:
    title: str
    description: str
    reporter_id: UUID


@dataclass(frozen=True, kw_only=True)
class AssignTicketCommand:
    ticket_id: UUID
    assignee_id: UUID

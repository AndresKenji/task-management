from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.domain import DomainEvent


@dataclass(frozen=True, kw_only=True)
class TicketCreated(DomainEvent):
    ticket_id: UUID
    title: str
    reporter_id: UUID


@dataclass(frozen=True, kw_only=True)
class TicketAssigned(DomainEvent):
    ticket_id: UUID
    assignee_id: UUID


@dataclass(frozen=True, kw_only=True)
class TicketClosed(DomainEvent):
    ticket_id: UUID

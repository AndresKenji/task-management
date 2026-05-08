from __future__ import annotations

from uuid import UUID

from tickets.application import TicketRepository
from tickets.domain import Ticket


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self._tickets: dict[UUID, Ticket] = {}

    def add(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def get(self, ticket_id: UUID) -> Ticket:
        if ticket_id not in self._tickets:
            raise KeyError(f"ticket {ticket_id} not found")
        return self._tickets[ticket_id]

    def list_all(self) -> list[Ticket]:
        return list(self._tickets.values())

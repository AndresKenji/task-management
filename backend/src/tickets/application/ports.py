from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from tickets.domain import Ticket


class TicketRepository(ABC):
    @abstractmethod
    def add(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def get(self, ticket_id: UUID) -> Ticket: ...

    @abstractmethod
    def list_all(self) -> list[Ticket]: ...

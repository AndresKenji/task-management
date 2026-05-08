from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from tickets.domain import Ticket


class TicketRepository(ABC):
    @abstractmethod
    async def add(self, ticket: Ticket) -> None: ...

    @abstractmethod
    async def get(self, ticket_id: UUID) -> Ticket: ...

    @abstractmethod
    async def list_all(self) -> list[Ticket]: ...

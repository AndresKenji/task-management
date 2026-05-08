from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tickets.application import TicketRepository
from tickets.domain import Ticket

from .models import TicketModel, domain_to_model, model_to_domain


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, ticket: Ticket) -> None:
        await self._session.merge(domain_to_model(ticket))

    async def get(self, ticket_id: UUID) -> Ticket:
        model = await self._session.get(TicketModel, ticket_id)
        if model is None:
            raise KeyError(f"ticket {ticket_id} not found")
        return model_to_domain(model)

    async def list_all(self) -> list[Ticket]:
        result = await self._session.execute(select(TicketModel))
        return [model_to_domain(m) for m in result.scalars().all()]

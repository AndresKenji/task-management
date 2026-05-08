from __future__ import annotations

from uuid import uuid4

from tickets.application import (
    AssignTicket,
    AssignTicketCommand,
    CreateTicket,
    CreateTicketCommand,
)
from tickets.domain import TicketStatus
from tickets.infrastructure import InMemoryTicketRepository


class TestCreateTicket:
    async def test_persists_ticket_and_returns_id(self) -> None:
        repo = InMemoryTicketRepository()
        use_case = CreateTicket(repo)

        ticket_id = await use_case.execute(
            CreateTicketCommand(
                title="DB migration failed",
                description="Alembic upgrade head crashed in staging.",
                reporter_id=uuid4(),
            )
        )

        ticket = await repo.get(ticket_id)
        assert ticket.id == ticket_id
        assert ticket.status == TicketStatus.OPEN


class TestAssignTicket:
    async def test_assignment_is_persisted(self) -> None:
        repo = InMemoryTicketRepository()
        create = CreateTicket(repo)
        assign = AssignTicket(repo)

        ticket_id = await create.execute(
            CreateTicketCommand(title="x", description="y", reporter_id=uuid4())
        )
        assignee_id = uuid4()

        await assign.execute(AssignTicketCommand(ticket_id=ticket_id, assignee_id=assignee_id))

        ticket = await repo.get(ticket_id)
        assert ticket.assignee_id == assignee_id
        assert ticket.status == TicketStatus.IN_PROGRESS

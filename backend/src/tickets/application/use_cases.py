from __future__ import annotations

from uuid import UUID

from tickets.domain import Ticket

from .commands import AssignTicketCommand, CreateTicketCommand
from .ports import TicketRepository


class CreateTicket:
    def __init__(self, repo: TicketRepository) -> None:
        self._repo = repo

    def execute(self, cmd: CreateTicketCommand) -> UUID:
        ticket = Ticket.create(
            title=cmd.title,
            description=cmd.description,
            reporter_id=cmd.reporter_id,
        )
        self._repo.add(ticket)
        return ticket.id


class AssignTicket:
    def __init__(self, repo: TicketRepository) -> None:
        self._repo = repo

    def execute(self, cmd: AssignTicketCommand) -> None:
        # TODO(milestone-2): implement.
        # Steps:
        #   1. Load the ticket: ticket = self._repo.get(cmd.ticket_id).
        #   2. Apply the domain rule: ticket.assign(cmd.assignee_id).
        #   3. Persist: self._repo.add(ticket). The in-memory repo treats add() as
        #      an upsert; the SQLAlchemy version (milestone 3) will too.
        # No return value needed.
        raise NotImplementedError

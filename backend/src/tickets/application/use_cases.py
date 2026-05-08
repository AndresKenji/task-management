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
        ticket: Ticket = self._repo.get(cmd.ticket_id)
        ticket.assign(cmd.assignee_id)
        self._repo.add(ticket)

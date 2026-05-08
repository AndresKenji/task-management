from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from shared.domain import AggregateRoot, new_id

from .events import TicketCreated
from .value_objects import TicketStatus


class Ticket(AggregateRoot):
    def __init__(
        self,
        *,
        id: UUID,
        title: str,
        description: str,
        reporter_id: UUID,
        status: TicketStatus,
        assignee_id: UUID | None,
        created_at: datetime,
    ) -> None:
        super().__init__(id)
        self._title = title
        self._description = description
        self._reporter_id = reporter_id
        self._status = status
        self._assignee_id = assignee_id
        self._created_at = created_at

    @classmethod
    def create(cls, *, title: str, description: str, reporter_id: UUID) -> Ticket:
        if not title.strip():
            raise ValueError("title must not be empty")
        ticket = cls(
            id=new_id(),
            title=title,
            description=description,
            reporter_id=reporter_id,
            status=TicketStatus.OPEN,
            assignee_id=None,
            created_at=datetime.now(timezone.utc),
        )
        ticket._record(
            TicketCreated(
                ticket_id=ticket.id,
                title=ticket._title,
                reporter_id=ticket._reporter_id,
            )
        )
        return ticket

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def reporter_id(self) -> UUID:
        return self._reporter_id

    @property
    def status(self) -> TicketStatus:
        return self._status

    @property
    def assignee_id(self) -> UUID | None:
        return self._assignee_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def assign(self, assignee_id: UUID) -> None:
        # TODO(milestone-2): implement assignment. Rules:
        #   - status CLOSED: raise ValueError("cannot assign a closed ticket").
        #   - status OPEN: transition to IN_PROGRESS.
        #   - status IN_PROGRESS: leave status as-is (reassign allowed).
        #   - Update self._assignee_id and record a TicketAssigned event
        #     (import from .events) via self._record(...).
        raise NotImplementedError

    def close(self) -> None:
        # TODO(milestone-2): implement closing. Rules:
        #   - status CLOSED: raise ValueError("ticket is already closed").
        #   - otherwise: transition to CLOSED and record a TicketClosed event.
        raise NotImplementedError

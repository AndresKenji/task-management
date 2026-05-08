from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.orm import Base
from tickets.domain import Ticket, TicketStatus


class TicketModel(Base):
    __tablename__ = "tickets"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    reporter_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    assignee_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def model_to_domain(model: TicketModel) -> Ticket:
    return Ticket(
        id=model.id,
        title=model.title,
        description=model.description,
        reporter_id=model.reporter_id,
        status=TicketStatus(model.status),
        assignee_id=model.assignee_id,
        created_at=model.created_at,
    )


def domain_to_model(ticket: Ticket) -> TicketModel:
    return TicketModel(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        reporter_id=ticket.reporter_id,
        status=ticket.status.value,
        assignee_id=ticket.assignee_id,
        created_at=ticket.created_at,
    )

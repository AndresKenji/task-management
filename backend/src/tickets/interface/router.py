from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from shared.infrastructure import UnitOfWork, get_uow
from tickets.application import CreateTicket, CreateTicketCommand, AssignTicket, AssignTicketCommand
from tickets.infrastructure import SqlAlchemyTicketRepository

from .schemas import AssignTicketIn, CreateTicketIn, TicketOut, ticket_to_out


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TicketOut)
async def create_ticket(
    payload: CreateTicketIn,
    uow: UnitOfWork = Depends(get_uow),
) -> TicketOut:
    async with uow:
        repo = SqlAlchemyTicketRepository(uow.session)
        use_case = CreateTicket(repo)
        ticket_id = await use_case.execute(
            CreateTicketCommand(
                title=payload.title,
                description=payload.description,
                reporter_id=payload.reporter_id,
            )
        )
        ticket = await repo.get(ticket_id)
    return ticket_to_out(ticket)


@router.get("", response_model=list[TicketOut])
async def list_tickets(uow: UnitOfWork = Depends(get_uow)) -> list[TicketOut]:
    async with uow:
        repo = SqlAlchemyTicketRepository(uow.session)
        tickets = await repo.list_all()
    return [ticket_to_out(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> TicketOut:
    async with uow:
        repo = SqlAlchemyTicketRepository(uow.session)
        try:
            ticket = await repo.get(ticket_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="ticket not found")
    return ticket_to_out(ticket)


@router.post("/{ticket_id}/assign", response_model=TicketOut)
async def assign_ticket(
    ticket_id: UUID,
    payload: AssignTicketIn,
    uow: UnitOfWork = Depends(get_uow),
) -> TicketOut:
    async with uow:
        repo = SqlAlchemyTicketRepository(uow.session)
        use_case = AssignTicket(repo)
        try:
            await use_case.execute(
                AssignTicketCommand(
                    ticket_id=ticket_id,
                    assignee_id=payload.assignee_id,
                )
            )
            ticket = await repo.get(ticket_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="ticket not found")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    return ticket_to_out(ticket)


__all__ = ["router"]

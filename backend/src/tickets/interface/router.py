from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from shared.infrastructure import UnitOfWork, get_uow
from tickets.application import CreateTicket, CreateTicketCommand
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
    # TODO(milestone-3): implement.
    # Steps:
    #   1. async with uow: open the unit of work.
    #   2. repo = SqlAlchemyTicketRepository(uow.session)
    #   3. tickets = await repo.list_all()
    #   4. return [ticket_to_out(t) for t in tickets]
    raise NotImplementedError


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> TicketOut:
    # TODO(milestone-3): implement.
    # Steps:
    #   1. async with uow.
    #   2. repo = SqlAlchemyTicketRepository(uow.session)
    #   3. try: ticket = await repo.get(ticket_id)
    #      except KeyError: raise HTTPException(status_code=404, detail="ticket not found")
    #   4. return ticket_to_out(ticket).
    raise NotImplementedError


@router.post("/{ticket_id}/assign", response_model=TicketOut)
async def assign_ticket(
    ticket_id: UUID,
    payload: AssignTicketIn,
    uow: UnitOfWork = Depends(get_uow),
) -> TicketOut:
    # TODO(milestone-3): implement.
    # Steps:
    #   1. async with uow.
    #   2. repo = SqlAlchemyTicketRepository(uow.session); build AssignTicket use case.
    #   3. try: await use_case.execute(AssignTicketCommand(ticket_id=ticket_id,
    #          assignee_id=payload.assignee_id))
    #      except KeyError: 404 "ticket not found"
    #      except ValueError as e: 409 str(e)  (covers "cannot assign a closed ticket")
    #   4. ticket = await repo.get(ticket_id); return ticket_to_out(ticket).
    raise NotImplementedError


__all__ = ["router"]

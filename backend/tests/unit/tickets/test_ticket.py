from __future__ import annotations

from uuid import uuid4

import pytest

from tickets.domain import Ticket, TicketCreated, TicketStatus


class TestTicketCreate:
    def test_creates_open_ticket_with_event(self) -> None:
        reporter_id = uuid4()

        ticket = Ticket.create(
            title="Login button broken",
            description="Clicking login does nothing on Safari.",
            reporter_id=reporter_id,
        )

        assert ticket.title == "Login button broken"
        assert ticket.description == "Clicking login does nothing on Safari."
        assert ticket.reporter_id == reporter_id
        assert ticket.status == TicketStatus.OPEN
        assert ticket.assignee_id is None

        events = ticket.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], TicketCreated)
        assert events[0].ticket_id == ticket.id

    def test_rejects_empty_title(self) -> None:
        with pytest.raises(ValueError):
            Ticket.create(title="   ", description="x", reporter_id=uuid4())


class TestTicketAssign:
    @pytest.mark.skip(reason="TODO milestone-2: implement Ticket.assign() then enable")
    def test_assigning_open_ticket_moves_to_in_progress(self) -> None:
        # Hint: create a ticket, ticket.pull_events() to clear the TicketCreated,
        # then ticket.assign(uuid4()) and assert status, assignee_id, and that
        # pull_events() now returns a single TicketAssigned for ticket.id.
        ...

    @pytest.mark.skip(reason="TODO milestone-2")
    def test_reassigning_in_progress_keeps_status_and_swaps_assignee(self) -> None:
        # Hint: assign once, pull_events, assign a different uuid, assert status
        # is still IN_PROGRESS and assignee_id is the new one.
        ...

    @pytest.mark.skip(reason="TODO milestone-2")
    def test_assigning_closed_ticket_raises(self) -> None:
        # Hint: create -> close -> assign should raise ValueError. Use pytest.raises.
        ...


class TestTicketClose:
    @pytest.mark.skip(reason="TODO milestone-2: implement Ticket.close() then enable")
    def test_closing_open_ticket_records_event(self) -> None:
        # Hint: create, pull_events, close, assert status is CLOSED and that
        # pull_events returns a TicketClosed.
        ...

    @pytest.mark.skip(reason="TODO milestone-2")
    def test_closing_already_closed_raises(self) -> None:
        # Hint: close twice; the second call should raise ValueError.
        ...

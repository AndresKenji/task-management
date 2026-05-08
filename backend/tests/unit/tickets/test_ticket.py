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
    def test_assigning_open_ticket_moves_to_in_progress(self) -> None:
        ticket = Ticket.create(
            title="Login button broken",
            description="Clicking login does nothing on Safari.",
            reporter_id=uuid4(),
        )
        _ = ticket.pull_events()
        assignee_id = uuid4()
        ticket.assign(assignee_id)
        assert ticket.status == TicketStatus.IN_PROGRESS
        assert ticket.assignee_id is not None
        events = ticket.pull_events()
        assert len(events) == 1
        assert events[0].ticket_id == ticket.id
        assert events[0].assignee_id == assignee_id

    def test_reassigning_in_progress_keeps_status_and_swaps_assignee(self) -> None:
        ticket = Ticket.create(
            title="User profile picture not uploading",
            description="Users cannot upload profile pictures on mobile.",
            reporter_id=uuid4(),
        )
        _ = ticket.pull_events()
        first_assignee_id = uuid4()
        ticket.assign(first_assignee_id)
        _ = ticket.pull_events()
        second_assignee_id = uuid4()
        ticket.assign(second_assignee_id)
        assert ticket.status == TicketStatus.IN_PROGRESS
        assert ticket.assignee_id == second_assignee_id

    def test_assigning_closed_ticket_raises(self) -> None:
        ticket = Ticket.create(
            title="Password reset email not sent",
            description="Users do not receive password reset emails.",
            reporter_id=uuid4(),
        )
        _ = ticket.pull_events()
        ticket.close()
        ticket.pull_events()
        with pytest.raises(ValueError):
            ticket.assign(uuid4())


class TestTicketClose:
    def test_closing_open_ticket_records_event(self) -> None:
        ticket = Ticket.create(
            title="Database backup failing",
            description="The daily database backup job fails with a timeout error.",
            reporter_id=uuid4(),
        )
        _ = ticket.pull_events()
        ticket.close()
        assert ticket.status == TicketStatus.CLOSED
        events = ticket.pull_events()
        assert len(events) == 1
        assert events[0].ticket_id == ticket.id

    def test_closing_already_closed_raises(self) -> None:
        ticket = Ticket.create(
            title="Database backup failing",
            description="The daily database backup job fails with a timeout error.",
            reporter_id=uuid4(),
        )
        _ = ticket.pull_events()
        ticket.close()
        with pytest.raises(ValueError):
            ticket.close()

from __future__ import annotations

from uuid import uuid4

import pytest


pytestmark = pytest.mark.integration


class TestCreateTicket:
    async def test_create_returns_201_with_ticket_payload(self, client) -> None:
        reporter_id = str(uuid4())

        response = await client.post(
            "/tickets",
            json={
                "title": "Login fails on Safari",
                "description": "OAuth callback hangs.",
                "reporter_id": reporter_id,
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Login fails on Safari"
        assert body["status"] == "open"
        assert body["reporter_id"] == reporter_id
        assert body["assignee_id"] is None


class TestListTickets:
    @pytest.mark.skip(reason="TODO milestone-3: implement GET /tickets handler then enable")
    async def test_list_returns_created_tickets(self, client) -> None:
        # Hint: POST two tickets with different titles, then GET /tickets.
        # Assert the response is a list of length 2 containing both titles.
        ...


class TestGetTicket:
    @pytest.mark.skip(reason="TODO milestone-3: implement GET /tickets/{id} handler then enable")
    async def test_get_existing_returns_200(self, client) -> None:
        # Hint: POST a ticket, capture body["id"], GET /tickets/{id}, assert 200
        # and that the body matches what was created.
        ...

    @pytest.mark.skip(reason="TODO milestone-3")
    async def test_get_missing_returns_404(self, client) -> None:
        # Hint: GET /tickets/{random uuid} should return 404.
        ...


class TestAssignTicket:
    @pytest.mark.skip(reason="TODO milestone-3: implement POST /tickets/{id}/assign then enable")
    async def test_assign_moves_open_ticket_to_in_progress(self, client) -> None:
        # Hint: POST a ticket; POST /tickets/{id}/assign with {"assignee_id": ...};
        # assert response status is 200 and body shows status "in_progress" plus
        # the new assignee_id.
        ...

    @pytest.mark.skip(reason="TODO milestone-3")
    async def test_assign_missing_returns_404(self, client) -> None:
        # Hint: POST /tickets/{random uuid}/assign should return 404.
        ...

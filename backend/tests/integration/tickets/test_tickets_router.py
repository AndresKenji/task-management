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
    async def test_list_returns_created_tickets(self, client) -> None:
        reporter_id = str(uuid4())

        await client.post(
            "/tickets",
            json={
                "title": "Login fails on Safari",
                "description": "OAuth callback hangs.",
                "reporter_id": reporter_id,
            },
        )
        await client.post(
            "/tickets",
            json={
                "title": "Page crashes on mobile",
                "description": "Touching the button causes a crash.",
                "reporter_id": reporter_id,
            },
        )
        response = await client.get("/tickets")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 2


class TestGetTicket:
    async def test_get_existing_returns_200(self, client) -> None:
        reporter_id = str(uuid4())

        await client.post(
            "/tickets",
            json={
                "title": "Login fails on Safari",
                "description": "OAuth callback hangs.",
                "reporter_id": reporter_id,
            },
        )
        response = await client.get("/tickets")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        ticket_id = body[0]["id"]
        response = await client.get(f"/tickets/{ticket_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == ticket_id
        assert body["title"] == "Login fails on Safari"
        assert body["description"] == "OAuth callback hangs."
        assert body["reporter_id"] == reporter_id
        assert body["assignee_id"] is None
        assert body["status"] == "open"

    async def test_get_missing_returns_404(self, client) -> None:
        random_uuid = str(uuid4())
        response = await client.get(f"/tickets/{random_uuid}")
        assert response.status_code == 404


class TestAssignTicket:
    async def test_assign_moves_open_ticket_to_in_progress(self, client) -> None:
        reporter_id = str(uuid4())
        user_id = str(uuid4())

        ticket = await client.post(
            "/tickets",
            json={
                "title": "Login fails on Safari",
                "description": "OAuth callback hangs.",
                "reporter_id": reporter_id,
            },
        )
        response = await client.post(
            f"/tickets/{ticket.json()['id']}/assign",
            json={"assignee_id": user_id},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "in_progress"
        assert body["assignee_id"] == user_id

    async def test_assign_missing_returns_404(self, client) -> None:
        random_uuid = str(uuid4())
        response = await client.post(
            f"/tickets/{random_uuid}/assign",
            json={"assignee_id": str(uuid4())},
        )
        assert response.status_code == 404

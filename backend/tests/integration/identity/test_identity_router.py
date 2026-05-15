from __future__ import annotations

import pytest


pytestmark = pytest.mark.integration


class TestGetMyProfile:
    async def test_returns_profile_for_authenticated_user(self, client) -> None:
        response = await client.get("/users/me")
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "dev@example.com"
        assert body["full_name"] == "Dev User"

    async def test_second_request_returns_same_user(self, client) -> None:
        response1 = await client.get("/users/me")
        assert response1.status_code == 200
        body1 = response1.json()
        response2 = await client.get("/users/me")
        assert response2.status_code == 200
        body2 = response2.json()
        assert body1["id"] == body2["id"]

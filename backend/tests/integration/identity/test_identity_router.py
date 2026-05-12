from __future__ import annotations

import pytest


pytestmark = pytest.mark.integration


class TestGetMyProfile:
    @pytest.mark.skip(reason="TODO milestone-4: implement GET /users/me handler then enable")
    async def test_returns_profile_for_authenticated_user(self, client) -> None:
        # Hint: GET /users/me. With the fake current_user dependency the response
        # should be 200 and the body should contain dev@example.com and "Dev User".
        ...

    @pytest.mark.skip(reason="TODO milestone-4")
    async def test_second_request_returns_same_user(self, client) -> None:
        # Hint: GET /users/me twice. Both responses should return the same id,
        # which proves the second call hits the existing-user branch of
        # GetOrCreateProfile rather than creating a duplicate.
        ...

from __future__ import annotations

from uuid import uuid4

import pytest

from identity.application import GetOrCreateProfile, GetOrCreateProfileCommand
from identity.infrastructure import InMemoryUserRepository


class TestGetOrCreateProfile:
    @pytest.mark.skip(reason="TODO milestone-4: implement GetOrCreateProfile.execute then enable")
    async def test_creates_user_when_missing(self) -> None:
        repo = InMemoryUserRepository()
        use_case = GetOrCreateProfile(repo)
        sub = uuid4()

        user = await use_case.execute(
            GetOrCreateProfileCommand(
                sub=sub,
                email="alice@example.com",
                full_name="Alice",
            )
        )

        assert user.id == sub
        assert user.email == "alice@example.com"
        assert user.full_name == "Alice"

        from_repo = await repo.get(sub)
        assert from_repo.id == sub

    @pytest.mark.skip(reason="TODO milestone-4: write the existing-user path test")
    async def test_returns_existing_user_when_present(self) -> None:
        # Hint:
        #   1. Build the repo and pre-populate it with a User via User.create(...) + repo.add(...).
        #   2. Call use_case.execute with the same sub but a different email/full_name.
        #   3. Assert the returned user has the ORIGINAL email/full_name (not the input ones).
        #      That confirms we hit the existing-user branch rather than overwriting.
        ...

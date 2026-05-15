from __future__ import annotations

from uuid import uuid4

from identity.application import GetOrCreateProfile, GetOrCreateProfileCommand
from identity.infrastructure import InMemoryUserRepository
from identity.domain import User


class TestGetOrCreateProfile:
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

    async def test_returns_existing_user_when_present(self) -> None:
        repo = InMemoryUserRepository()
        use_case = GetOrCreateProfile(repo)
        sub = uuid4()
        existing_user = User.create(sub=sub, email="kenji@example.com", full_name="Kenji")
        await repo.add(existing_user)
        result = await use_case.execute(
            GetOrCreateProfileCommand(
                sub=sub,
                email="impostor@example.com",
                full_name="Impostor",
            )
        )
        assert result.email == "kenji@example.com"
        assert result.full_name == "Kenji"

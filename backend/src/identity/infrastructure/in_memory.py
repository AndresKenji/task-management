from __future__ import annotations

from uuid import UUID

from identity.application import UserRepository
from identity.domain import User


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        self._users[user.id] = user

    async def get(self, user_id: UUID) -> User:
        if user_id not in self._users:
            raise KeyError(f"user {user_id} not found")
        return self._users[user_id]

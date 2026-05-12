from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from identity.domain import User


class UserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def get(self, user_id: UUID) -> User: ...

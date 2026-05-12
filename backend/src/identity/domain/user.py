from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from shared.domain import AggregateRoot

from .events import UserCreated


class User(AggregateRoot):
    def __init__(
        self,
        *,
        id: UUID,
        email: str,
        full_name: str,
        created_at: datetime,
    ) -> None:
        super().__init__(id)
        self._email = email
        self._full_name = full_name
        self._created_at = created_at

    @classmethod
    def create(cls, *, sub: UUID, email: str, full_name: str) -> User:
        if not email.strip():
            raise ValueError("email must not be empty")
        user = cls(
            id=sub,
            email=email,
            full_name=full_name,
            created_at=datetime.now(timezone.utc),
        )
        user._record(
            UserCreated(
                user_id=sub,
                email=email,
                full_name=full_name,
            )
        )
        return user

    @property
    def email(self) -> str:
        return self._email

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def created_at(self) -> datetime:
        return self._created_at

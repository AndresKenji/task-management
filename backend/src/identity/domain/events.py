from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.domain import DomainEvent


@dataclass(frozen=True, kw_only=True)
class UserCreated(DomainEvent):
    user_id: UUID
    email: str
    full_name: str

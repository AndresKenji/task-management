from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class GetOrCreateProfileCommand:
    sub: UUID
    email: str
    full_name: str

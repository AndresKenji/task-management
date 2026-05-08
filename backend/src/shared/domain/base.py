from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, kw_only=True)
class ValueObject:
    pass


class Entity:
    def __init__(self, id: UUID) -> None:
        self._id = id

    @property
    def id(self) -> UUID:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash((type(self), self._id))


class AggregateRoot(Entity):
    def __init__(self, id: UUID) -> None:
        super().__init__(id)
        self._events: list[DomainEvent] = []

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = self._events
        self._events = []
        return events


def new_id() -> UUID:
    return uuid4()

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CognitoUser:
    sub: UUID
    email: str
    full_name: str
    groups: tuple[str, ...]


def current_user() -> CognitoUser:
    # TODO(milestone-7): replace with a dependency that reads claims from the
    # Lambda event (requestContext.authorizer.jwt.claims) once APIGW + Cognito
    # are wired up. Until then this returns a fixed dev identity.
    return CognitoUser(
        sub=UUID("00000000-0000-0000-0000-000000000001"),
        email="dev@example.com",
        full_name="Dev User",
        groups=("user",),
    )

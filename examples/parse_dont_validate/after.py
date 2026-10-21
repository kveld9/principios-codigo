"""Parse, don't validate: construct immutable typed domain models at the boundary."""

from dataclasses import dataclass
from typing import Any

SENIOR_AGE_THRESHOLD: int = 60
MINIMUM_ADULT_AGE: int = 18
ALLOWED_STATUSES: frozenset[str] = frozenset({"active", "pending", "suspended"})


class UserParsingError(ValueError):
    """Domain exception indicating boundary parsing failure with preserved cause."""


@dataclass(frozen=True)
class UserProfile:
    """Immutable domain model representing a validated, parsed user record."""

    user_id: int
    email: str
    age: int
    status: str


def _parse_user_id(raw_user_id: Any) -> int:
    """Parse and validate user identifier."""
    try:
        parsed_user_id = int(raw_user_id)
        if parsed_user_id <= 0:
            raise ValueError(f"user_id must be a positive integer, got: {parsed_user_id}")
        return parsed_user_id
    except (TypeError, ValueError) as error:
        raise UserParsingError(f"Failed to parse user_id '{raw_user_id}': {error}") from error


def _parse_email(raw_email: Any) -> str:
    """Parse and validate customer email string."""
    try:
        if not isinstance(raw_email, str) or "@" not in raw_email:
            raise ValueError(f"email must be a string containing '@', got: {raw_email}")
        return raw_email.strip()
    except ValueError as error:
        raise UserParsingError(f"Failed to parse email: {error}") from error


def _parse_age(raw_age: Any) -> int:
    """Parse and validate customer age requirement."""
    try:
        parsed_age = int(raw_age)
        if parsed_age < MINIMUM_ADULT_AGE:
            raise ValueError(f"age must be at least {MINIMUM_ADULT_AGE}, got: {parsed_age}")
        return parsed_age
    except (TypeError, ValueError) as error:
        raise UserParsingError(f"Failed to parse age: {error}") from error


def _parse_status(raw_status: Any) -> str:
    """Parse and validate user account status."""
    try:
        if raw_status not in ALLOWED_STATUSES:
            raise ValueError(f"status must be in {set(ALLOWED_STATUSES)}, got: {raw_status}")
        return str(raw_status)
    except ValueError as error:
        raise UserParsingError(f"Failed to parse status: {error}") from error


def parse_user_profile(payload: dict[str, Any]) -> UserProfile:
    """Parse a raw boundary dictionary once into a type-safe UserProfile entity."""
    if not isinstance(payload, dict):
        raise UserParsingError("Payload must be a dictionary")

    return UserProfile(
        user_id=_parse_user_id(payload.get("user_id")),
        email=_parse_email(payload.get("email")),
        age=_parse_age(payload.get("age")),
        status=_parse_status(payload.get("status")),
    )


def determine_senior_discount(user: UserProfile) -> bool:
    """Evaluate business eligibility directly on validated domain models."""
    return user.status == "active" and user.age >= SENIOR_AGE_THRESHOLD

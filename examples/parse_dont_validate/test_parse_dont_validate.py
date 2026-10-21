"""Tests verifying parse_dont_validate type-safety and exception chaining."""

from typing import Any

import pytest

from examples.parse_dont_validate.after import (
    UserParsingError,
    UserProfile,
    determine_senior_discount,
    parse_user_profile,
)
from examples.parse_dont_validate.before import process_user_pipeline as before_pipeline


def test_valid_payload_parses_into_typed_dataclass() -> None:
    """A well-formed dictionary parses once into an immutable UserProfile."""
    payload = {
        "user_id": "42",
        "email": "alice@example.com",
        "age": "25",
        "status": "active",
    }
    profile = parse_user_profile(payload)
    assert profile == UserProfile(
        user_id=42,
        email="alice@example.com",
        age=25,
        status="active",
    )
    assert not determine_senior_discount(profile)


def test_downstream_domain_logic_without_revalidation() -> None:
    """Downstream operations safely rely on type invariants established at boundary."""
    senior_user = UserProfile(
        user_id=1,
        email="senior@example.com",
        age=65,
        status="active",
    )
    assert determine_senior_discount(senior_user)


@pytest.mark.parametrize(
    ("invalid_payload", "failing_field"),
    [
        ({"user_id": "-1", "email": "a@b.com", "age": 20, "status": "active"}, "user_id"),
        ({"user_id": "invalid", "email": "a@b.com", "age": 20, "status": "active"}, "user_id"),
        ({"user_id": 1, "email": "not-an-email", "age": 20, "status": "active"}, "email"),
        ({"user_id": 1, "email": "a@b.com", "age": 15, "status": "active"}, "age"),
        ({"user_id": 1, "email": "a@b.com", "age": "not-a-number", "status": "active"}, "age"),
        ({"user_id": 1, "email": "a@b.com", "age": 20, "status": "banned"}, "status"),
    ],
)
def test_invalid_fields_raise_domain_error_with_chained_cause(
    invalid_payload: dict[str, Any],
    failing_field: str,
) -> None:
    """Each malformed field raises UserParsingError and preserves the original cause."""
    with pytest.raises(UserParsingError) as exception_info:
        parse_user_profile(invalid_payload)

    assert failing_field in str(exception_info.value)
    assert exception_info.value.__cause__ is not None
    assert isinstance(exception_info.value.__cause__, (TypeError, ValueError))


def test_before_swallows_exceptions_and_loses_root_cause() -> None:
    """Anti-pattern silently swallows parsing errors, returning generic None or fallback."""
    corrupted_data = {"user_id": "abc", "email": "bad", "age": -5}
    result = before_pipeline(corrupted_data)
    assert result["success"] is False
    assert "error" in result

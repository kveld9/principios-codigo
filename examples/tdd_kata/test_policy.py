"""Tests driving password policy implementation via strict TDD."""

from examples.tdd_kata.policy import Violation, check_password


def test_valid_password_returns_empty_violation_list() -> None:
    """A password satisfying all criteria produces an empty violations list."""
    result = check_password("ValidPassword123")
    assert result == []


def test_too_short_password_returns_too_short_violation() -> None:
    """A password with length less than 12 characters reports TOO_SHORT."""
    result = check_password("Short1Aa")
    assert result == [Violation.TOO_SHORT]


def test_missing_digit_returns_missing_digit_violation() -> None:
    """A password lacking numerical characters reports MISSING_DIGIT."""
    result = check_password("PasswordWithoutDigit")
    assert result == [Violation.MISSING_DIGIT]


def test_missing_uppercase_returns_missing_uppercase_violation() -> None:
    """A password lacking uppercase letters reports MISSING_UPPERCASE."""
    result = check_password("lowercasepassword123")
    assert result == [Violation.MISSING_UPPERCASE]


def test_missing_lowercase_returns_missing_lowercase_violation() -> None:
    """A password lacking lowercase letters reports MISSING_LOWERCASE."""
    result = check_password("UPPERCASEPASSWORD123")
    assert result == [Violation.MISSING_LOWERCASE]


def test_multiple_violations_reported_in_declaration_order() -> None:
    """Multiple failing criteria report violations in strict declaration order."""
    # "short" has length < 12, no digits, no uppercase
    result = check_password("short")
    expected = [
        Violation.TOO_SHORT,
        Violation.MISSING_DIGIT,
        Violation.MISSING_UPPERCASE,
    ]
    assert result == expected


def test_completely_empty_password_reports_all_violations() -> None:
    """An empty password triggers every single violation in declaration order."""
    result = check_password("")
    expected = [
        Violation.TOO_SHORT,
        Violation.MISSING_DIGIT,
        Violation.MISSING_UPPERCASE,
        Violation.MISSING_LOWERCASE,
    ]
    assert result == expected

"""Password validation policy domain module."""

from collections.abc import Callable
from enum import Enum


class Violation(Enum):
    """Password validation violation categories in standard evaluation order."""

    TOO_SHORT = "TOO_SHORT"
    MISSING_DIGIT = "MISSING_DIGIT"
    MISSING_UPPERCASE = "MISSING_UPPERCASE"
    MISSING_LOWERCASE = "MISSING_LOWERCASE"


MINIMUM_PASSWORD_LENGTH: int = 12

PASSWORD_RULES: tuple[tuple[Violation, Callable[[str], bool]], ...] = (
    (Violation.TOO_SHORT, lambda password: len(password) < MINIMUM_PASSWORD_LENGTH),
    (
        Violation.MISSING_DIGIT,
        lambda password: not any(character.isdigit() for character in password),
    ),
    (
        Violation.MISSING_UPPERCASE,
        lambda password: not any(character.isupper() for character in password),
    ),
    (
        Violation.MISSING_LOWERCASE,
        lambda password: not any(character.islower() for character in password),
    ),
)


def check_password(password: str) -> list[Violation]:
    """Evaluate password against security requirements in strict declaration order."""
    return [violation for violation, predicate in PASSWORD_RULES if predicate(password)]

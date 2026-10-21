"""Anti-pattern: Tight coupling to concrete storage and business logic reading os.environ.

In this anti-pattern, the domain service instantiates an infrastructure database directly
in its constructor, making isolated unit testing impossible without monkeypatching or mocks.
Additionally, business logic directly accesses os.environ inside transaction methods, hiding
configuration dependencies and binding business decisions to process-level environment state.
"""

import os
from typing import Any


class ConcreteDatabase:
    """Concrete persistence infrastructure tightly coupled to internal storage."""

    def __init__(self) -> None:
        self.data: dict[str, dict[str, Any]] = {}

    def insert(self, record: dict[str, Any]) -> None:
        """Insert a record into the concrete table."""
        self.data[record["id"]] = record

    def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Find a record by identifier."""
        return self.data.get(user_id)


class UserService:
    """Service mixing business rules with infrastructure and environment access."""

    def __init__(self) -> None:
        # Anti-pattern: direct instantiation of infrastructure dependency
        self.db = ConcreteDatabase()

    def register_user(self, user_id: str, email: str) -> dict[str, Any]:
        """Register a user while directly accessing global environment state."""
        # Anti-pattern: reading os.environ inside domain business logic
        allowed_domain = os.environ.get("APP_ALLOWED_DOMAIN")
        if allowed_domain and not email.endswith(f"@{allowed_domain}"):
            raise ValueError(f"Email domain must be @{allowed_domain}")

        default_role = os.environ.get("APP_DEFAULT_ROLE", "user")

        if self.db.find_by_id(user_id) is not None:
            raise ValueError(f"User with ID '{user_id}' already exists")

        record = {
            "id": user_id,
            "email": email,
            "role": default_role,
        }
        self.db.insert(record)
        return record

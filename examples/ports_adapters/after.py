"""Hexagonal architecture (ports and adapters) isolating domain from infrastructure."""

import os
from dataclasses import dataclass
from typing import Protocol

DEFAULT_ROLE_ENV_VAR: str = "APP_DEFAULT_ROLE"
ALLOWED_DOMAIN_ENV_VAR: str = "APP_ALLOWED_DOMAIN"


@dataclass(frozen=True)
class User:
    """Domain entity representing a registered system user."""

    user_id: str
    email: str
    role: str


class UserRepository(Protocol):
    """Port interface defining persistence operations required by the domain."""

    def save(self, user: User) -> None:
        """Persist a User entity."""
        ...

    def get_by_id(self, user_id: str) -> User | None:
        """Retrieve a User by identifier."""
        ...


class InMemoryUserRepository:
    """Adapter implementing UserRepository port using in-memory storage for testing."""

    def __init__(self) -> None:
        self._storage: dict[str, User] = {}

    def save(self, user: User) -> None:
        """Persist user in the in-memory map."""
        self._storage[user.user_id] = user

    def get_by_id(self, user_id: str) -> User | None:
        """Find user by identifier."""
        return self._storage.get(user_id)


class UserService:
    """Pure domain service depending solely on the UserRepository abstraction."""

    def __init__(
        self,
        repository: UserRepository,
        default_role: str = "user",
        allowed_domain: str | None = None,
    ) -> None:
        self._repository = repository
        self._default_role = default_role
        self._allowed_domain = allowed_domain

    def _validate_domain(self, email: str) -> None:
        """Ensure email belongs to the configured domain boundary."""
        if self._allowed_domain and not email.endswith(f"@{self._allowed_domain}"):
            raise ValueError(f"Email domain must be @{self._allowed_domain}")

    def _ensure_unique_id(self, user_id: str) -> None:
        """Verify user ID has not been previously claimed."""
        if self._repository.get_by_id(user_id) is not None:
            raise ValueError(f"User with ID '{user_id}' already exists")

    def register_user(self, user_id: str, email: str) -> User:
        """Register a user within domain invariants without knowing persistence details."""
        self._validate_domain(email)
        self._ensure_unique_id(user_id)

        user = User(user_id=user_id, email=email, role=self._default_role)
        self._repository.save(user)
        return user


def create_user_service(
    repository: UserRepository | None = None,
    default_role: str | None = None,
    allowed_domain: str | None = None,
) -> UserService:
    """Composition root: wire adapters and external configuration at the boundary."""
    resolved_repository = repository if repository is not None else InMemoryUserRepository()
    resolved_default_role = (
        default_role if default_role is not None else os.environ.get(DEFAULT_ROLE_ENV_VAR, "user")
    )
    resolved_allowed_domain = (
        allowed_domain if allowed_domain is not None else os.environ.get(ALLOWED_DOMAIN_ENV_VAR)
    )
    return UserService(
        repository=resolved_repository,
        default_role=resolved_default_role,
        allowed_domain=resolved_allowed_domain,
    )

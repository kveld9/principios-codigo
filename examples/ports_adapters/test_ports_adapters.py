"""Tests for the ports_adapters architectural pattern example."""

import pytest

from examples.ports_adapters.after import (
    InMemoryUserRepository,
    User,
    UserService,
    create_user_service,
)
from examples.ports_adapters.before import UserService as BeforeUserService


def test_before_user_service_registers_user(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify legacy service registers user but requires environment mutation."""
    monkeypatch.setenv("APP_DEFAULT_ROLE", "member")
    monkeypatch.setenv("APP_ALLOWED_DOMAIN", "company.com")

    service = BeforeUserService()
    result = service.register_user("USR-01", "dev@company.com")
    assert result["id"] == "USR-01"
    assert result["email"] == "dev@company.com"
    assert result["role"] == "member"


def test_after_user_service_registration_with_in_memory_adapter() -> None:
    """Verify domain service operates purely through protocol port without mocks."""
    repository = InMemoryUserRepository()
    service = UserService(repository=repository, default_role="editor")

    created = service.register_user("USR-10", "author@example.com")
    persisted = repository.get_by_id("USR-10")

    assert created == User(user_id="USR-10", email="author@example.com", role="editor")
    assert persisted == created


def test_after_user_service_enforces_domain_constraints() -> None:
    """Verify business invariant checks on email domain and duplicate IDs."""
    repository = InMemoryUserRepository()
    service = UserService(repository=repository, allowed_domain="trusted.org")

    with pytest.raises(ValueError, match="domain must be @trusted.org"):
        service.register_user("USR-20", "user@untrusted.com")

    service.register_user("USR-20", "user@trusted.org")
    with pytest.raises(ValueError, match="already exists"):
        service.register_user("USR-20", "user@trusted.org")


def test_composition_root_assembles_service_with_injected_parameters() -> None:
    """Verify composition root constructs valid service using explicit parameters."""
    repository = InMemoryUserRepository()
    service = create_user_service(
        repository=repository,
        default_role="admin",
        allowed_domain="root.internal",
    )
    user = service.register_user("ROOT-1", "admin@root.internal")
    assert user.role == "admin"
    assert repository.get_by_id("ROOT-1") == user


def test_composition_root_resolves_environment_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify composition root safely reads environment fallback at application boundary."""
    monkeypatch.setenv("APP_DEFAULT_ROLE", "viewer")
    monkeypatch.setenv("APP_ALLOWED_DOMAIN", "env.org")

    service = create_user_service()
    user = service.register_user("ENV-1", "staff@env.org")
    assert user.role == "viewer"

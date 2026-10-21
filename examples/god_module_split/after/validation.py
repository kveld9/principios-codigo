"""Validation rules ensuring business invariants for orders."""

from examples.god_module_split.after.models import OrderItem, OrderRequest


def _validate_order_id(order_id: str) -> None:
    """Validate order identifier format."""
    if not order_id:
        raise ValueError("Order ID must be a non-empty string")


def _validate_email(email: str) -> None:
    """Validate customer email structure."""
    if "@" not in email or "." not in email:
        raise ValueError("Invalid customer email address")


def _validate_items_list(items: list[OrderItem]) -> None:
    """Ensure order contains at least one item."""
    if not items:
        raise ValueError("Order must contain at least one item")


def validate_order_request(order: OrderRequest) -> None:
    """Run all validation checks against an inbound OrderRequest."""
    _validate_order_id(order.order_id)
    _validate_email(order.email)
    _validate_items_list(order.items)

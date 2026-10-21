"""Parsing layer translating raw dictionaries into structured order representations."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from examples.god_module_split.after.models import CustomerTier, OrderItem, OrderRequest


def _validate_raw_dict(item: Any, error_message: str) -> None:
    """Ensure the target input is a dictionary."""
    if not isinstance(item, dict):
        raise ValueError(error_message)


def _parse_sku(sku: Any) -> str:
    """Extract and validate item SKU identifier."""
    if not isinstance(sku, str) or not sku.strip():
        raise ValueError("Item SKU must be a non-empty string")
    return sku.strip()


def _parse_quantity(quantity: Any) -> int:
    """Extract and validate item quantity."""
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive integer")
    return quantity


def _parse_unit_price(price: Any) -> Decimal:
    """Extract and validate item price as a 2-decimal quantized Decimal."""
    if not isinstance(price, (int, float, str, Decimal)):
        raise ValueError("Unit price must be a numeric value")
    try:
        decimal_price = Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as error:
        raise ValueError("Unit price must be a non-negative number") from error
    if decimal_price < Decimal("0.00"):
        raise ValueError("Unit price must be a non-negative number")
    return decimal_price


def _parse_item(item: Any) -> OrderItem:
    """Parse a single line item dictionary into an OrderItem."""
    _validate_raw_dict(item, "Each item must be a dictionary")
    return OrderItem(
        sku=_parse_sku(item.get("sku")),
        quantity=_parse_quantity(item.get("quantity")),
        unit_price=_parse_unit_price(item.get("unit_price")),
    )


def _resolve_tier(raw_tier: Any) -> CustomerTier:
    """Convert raw tier value to CustomerTier enum."""
    try:
        return CustomerTier(str(raw_tier))
    except ValueError as error:
        raise ValueError(f"Unknown customer tier: {raw_tier}") from error


def _extract_items(raw_items: Any) -> list[OrderItem]:
    """Extract and parse items list."""
    if not isinstance(raw_items, list):
        raise ValueError("Order must contain at least one item")
    return [_parse_item(raw_item) for raw_item in raw_items]


def parse_order_payload(payload: dict[str, Any]) -> OrderRequest:
    """Deserialize a raw order payload into an OrderRequest model."""
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary")

    order_id = payload.get("order_id")
    email = payload.get("email")
    raw_tier = payload.get("customer_tier", "standard")

    return OrderRequest(
        order_id=str(order_id).strip() if isinstance(order_id, str) else "",
        email=str(email).strip().lower() if isinstance(email, str) else "",
        customer_tier=_resolve_tier(raw_tier),
        items=_extract_items(payload.get("items")),
        coupon_code=payload.get("coupon_code"),
    )

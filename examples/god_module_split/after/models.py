"""Domain models and value representations for order processing."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CustomerTier(StrEnum):
    """Customer loyalty tier determining baseline discount privileges."""

    STANDARD = "standard"
    SILVER = "silver"
    GOLD = "gold"


@dataclass(frozen=True)
class OrderItem:
    """Line item within an order request."""

    sku: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class OrderRequest:
    """Validated representation of an inbound customer order."""

    order_id: str
    email: str
    customer_tier: CustomerTier
    items: list[OrderItem]
    coupon_code: str | None


@dataclass(frozen=True)
class PricingSummary:
    """Computed monetary breakdown of an order using exact Decimal arithmetic."""

    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal


@dataclass(frozen=True)
class ProcessedOrder:
    """Completed order record with status and formatted notification."""

    order_id: str
    email: str
    customer_tier: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    status: str
    notification: str

"""Pricing and discount calculation logic for orders using exact Decimal arithmetic."""

from decimal import ROUND_HALF_UP, Decimal

from examples.god_module_split.after.models import (
    CustomerTier,
    OrderItem,
    OrderRequest,
    PricingSummary,
)

TIER_DISCOUNT_RATES: dict[CustomerTier, Decimal] = {
    CustomerTier.STANDARD: Decimal("0.00"),
    CustomerTier.SILVER: Decimal("0.05"),
    CustomerTier.GOLD: Decimal("0.10"),
}

COUPON_AMOUNTS: dict[str, Decimal] = {
    "DISCOUNT10": Decimal("10.00"),
    "DISCOUNT20": Decimal("20.00"),
}

TAX_RATE: Decimal = Decimal("0.21")


def _calculate_subtotal(items: list[OrderItem]) -> Decimal:
    """Calculate the raw items subtotal using exact Decimal accumulation."""
    subtotal = sum((item.quantity * item.unit_price for item in items), Decimal("0.00"))
    return subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _resolve_coupon_discount(coupon_code: str | None) -> Decimal:
    """Calculate fixed coupon deduction."""
    if coupon_code is None:
        return Decimal("0.00")
    if coupon_code in COUPON_AMOUNTS:
        return COUPON_AMOUNTS[coupon_code]
    raise ValueError(f"Invalid coupon code: {coupon_code}")


def calculate_pricing(order: OrderRequest) -> PricingSummary:
    """Compute subtotal, tier discount, coupon discount, tax, and final total."""
    subtotal = _calculate_subtotal(order.items)
    tier_rate = TIER_DISCOUNT_RATES.get(order.customer_tier, Decimal("0.00"))
    tier_discount = (subtotal * tier_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    coupon_discount = _resolve_coupon_discount(order.coupon_code)

    total_discount = min(tier_discount + coupon_discount, subtotal)
    discounted_subtotal = subtotal - total_discount
    tax_amount = (discounted_subtotal * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    final_total = (discounted_subtotal + tax_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return PricingSummary(
        subtotal=subtotal,
        discount=total_discount,
        tax=tax_amount,
        total=final_total,
    )

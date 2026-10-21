"""Anti-pattern: God module mixing parsing, validation, pricing, persistence, and notifications.

This monolithic implementation violates the Single Responsibility Principle by combining
raw payload deserialization, business validation rules, discount and tax pricing algorithms,
in-memory dictionary storage mutations, and plain-text notification formatting into a single unit.
"""

from typing import Any

# Global shared storage acting as an implicit persistence dependency
_ORDER_DATABASE: dict[str, dict[str, Any]] = {}


def reset_database() -> None:
    """Clear all stored orders from the in-memory database."""
    _ORDER_DATABASE.clear()


def get_stored_order(order_id: str) -> dict[str, Any] | None:
    """Retrieve an order record directly from the global storage."""
    return _ORDER_DATABASE.get(order_id)


def process_order(payload: dict[str, Any]) -> dict[str, Any]:
    """Process an order end-to-end within a single monolithic procedure."""
    # Step 1: Raw payload parsing
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary")

    raw_order_id = payload.get("order_id")
    raw_email = payload.get("email")
    raw_tier = payload.get("customer_tier", "standard")
    raw_items = payload.get("items")
    raw_coupon = payload.get("coupon_code")

    # Step 2: Validation logic
    if not isinstance(raw_order_id, str) or not raw_order_id.strip():
        raise ValueError("Order ID must be a non-empty string")
    order_id = raw_order_id.strip()

    if not isinstance(raw_email, str) or "@" not in raw_email or "." not in raw_email:
        raise ValueError("Invalid customer email address")
    email = raw_email.strip().lower()

    if raw_tier not in {"standard", "silver", "gold"}:
        raise ValueError(f"Unknown customer tier: {raw_tier}")
    customer_tier = raw_tier

    if not isinstance(raw_items, list) or len(raw_items) == 0:
        raise ValueError("Order must contain at least one item")

    parsed_items: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            raise ValueError("Each item must be a dictionary")
        sku = item.get("sku")
        qty = item.get("quantity")
        price = item.get("unit_price")

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("Item SKU must be a non-empty string")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Unit price must be a non-negative number")

        parsed_items.append(
            {
                "sku": sku.strip(),
                "quantity": qty,
                "unit_price": float(price),
            }
        )

    # Step 3: Pricing computation
    subtotal = sum(item["quantity"] * item["unit_price"] for item in parsed_items)

    tier_discount = 0.0
    if customer_tier == "silver":
        tier_discount = subtotal * 0.05
    elif customer_tier == "gold":
        tier_discount = subtotal * 0.10

    coupon_discount = 0.0
    if raw_coupon == "DISCOUNT10":
        coupon_discount = 10.0
    elif raw_coupon == "DISCOUNT20":
        coupon_discount = 20.0
    elif raw_coupon is not None:
        raise ValueError(f"Invalid coupon code: {raw_coupon}")

    total_discount = min(tier_discount + coupon_discount, subtotal)
    discounted_subtotal = subtotal - total_discount
    tax_amount = round(discounted_subtotal * 0.21, 2)
    final_total = round(discounted_subtotal + tax_amount, 2)

    # Step 4: In-memory persistence
    record = {
        "order_id": order_id,
        "email": email,
        "customer_tier": customer_tier,
        "items": parsed_items,
        "subtotal": round(subtotal, 2),
        "discount": round(total_discount, 2),
        "tax": tax_amount,
        "total": final_total,
        "status": "CONFIRMED",
    }
    _ORDER_DATABASE[order_id] = record

    # Step 5: Notification template formatting
    summary_lines = [
        f"- {it['sku']} x{it['quantity']} (${it['unit_price']:.2f})" for it in parsed_items
    ]
    items_block = "\n".join(summary_lines)
    notification_message = (
        f"Order Confirmation: {order_id}\n"
        f"Recipient: {email}\n"
        f"Tier: {customer_tier.capitalize()}\n"
        f"Items:\n{items_block}\n"
        f"Subtotal: ${subtotal:.2f}\n"
        f"Discount: ${total_discount:.2f}\n"
        f"Tax (21%): ${tax_amount:.2f}\n"
        f"Total: ${final_total:.2f}\n"
        f"Status: CONFIRMED"
    )

    return {
        "order_id": order_id,
        "email": email,
        "customer_tier": customer_tier,
        "subtotal": round(subtotal, 2),
        "discount": round(total_discount, 2),
        "tax": tax_amount,
        "total": final_total,
        "status": "CONFIRMED",
        "notification": notification_message,
    }

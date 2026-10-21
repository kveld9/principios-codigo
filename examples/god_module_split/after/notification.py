"""Notification message formatting for confirmed orders."""

from examples.god_module_split.after.models import OrderItem, OrderRequest, PricingSummary


def _format_item_line(item: OrderItem) -> str:
    """Format a single line item entry for the notification body."""
    return f"- {item.sku} x{item.quantity} (${item.unit_price:.2f})"


def format_notification(order: OrderRequest, pricing: PricingSummary) -> str:
    """Render a structured plain-text confirmation notification."""
    items_block = "\n".join(_format_item_line(item) for item in order.items)
    tier_name = order.customer_tier.value.capitalize()

    return (
        f"Order Confirmation: {order.order_id}\n"
        f"Recipient: {order.email}\n"
        f"Tier: {tier_name}\n"
        f"Items:\n{items_block}\n"
        f"Subtotal: ${pricing.subtotal:.2f}\n"
        f"Discount: ${pricing.discount:.2f}\n"
        f"Tax (21%): ${pricing.tax:.2f}\n"
        f"Total: ${pricing.total:.2f}\n"
        f"Status: CONFIRMED"
    )

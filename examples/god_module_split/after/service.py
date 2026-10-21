"""Application service coordinating the domain modules for order processing."""

from typing import Any

from examples.god_module_split.after.models import ProcessedOrder
from examples.god_module_split.after.notification import format_notification
from examples.god_module_split.after.parsing import parse_order_payload
from examples.god_module_split.after.pricing import calculate_pricing
from examples.god_module_split.after.storage import OrderRepository
from examples.god_module_split.after.validation import validate_order_request


class OrderProcessingService:
    """Orchestrates order parsing, validation, pricing, notification, and persistence."""

    def __init__(self, repository: OrderRepository | None = None) -> None:
        self._repository = repository or OrderRepository()

    @property
    def repository(self) -> OrderRepository:
        """Access the underlying repository instance."""
        return self._repository

    def process_order(self, payload: dict[str, Any]) -> ProcessedOrder:
        """Execute the order lifecycle pipeline."""
        order_request = parse_order_payload(payload)
        validate_order_request(order_request)
        pricing = calculate_pricing(order_request)
        notification_text = format_notification(order_request, pricing)

        processed = ProcessedOrder(
            order_id=order_request.order_id,
            email=order_request.email,
            customer_tier=order_request.customer_tier.value,
            subtotal=pricing.subtotal,
            discount=pricing.discount,
            tax=pricing.tax,
            total=pricing.total,
            status="CONFIRMED",
            notification=notification_text,
        )
        self._repository.save(processed)
        return processed

"""Public facade exporting the service and composition root for order processing."""

from examples.god_module_split.after.service import OrderProcessingService
from examples.god_module_split.after.storage import OrderRepository


def build_order_service(
    repository: OrderRepository | None = None,
) -> OrderProcessingService:
    """Composition root: assemble an OrderProcessingService with an optional repository."""
    return OrderProcessingService(repository=repository)


__all__ = ["OrderProcessingService", "build_order_service"]

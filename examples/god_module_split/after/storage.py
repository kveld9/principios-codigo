"""In-memory persistence repository for processed orders."""

from examples.god_module_split.after.models import ProcessedOrder


class OrderRepository:
    """Encapsulated storage for persisting processed order records."""

    def __init__(self) -> None:
        self._records: dict[str, ProcessedOrder] = {}

    def save(self, order: ProcessedOrder) -> None:
        """Persist a processed order entity."""
        self._records[order.order_id] = order

    def get(self, order_id: str) -> ProcessedOrder | None:
        """Retrieve a processed order entity by ID."""
        return self._records.get(order_id)

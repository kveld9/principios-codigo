"""Differential and behavior tests for the god_module_split example."""

from decimal import Decimal
from typing import Any

import pytest

from examples.god_module_split import before
from examples.god_module_split.after import (
    OrderRepository,
    build_order_service,
)
from examples.god_module_split.after.models import ProcessedOrder

PARAMETRIZED_ORDERS: list[dict[str, Any]] = [
    {
        "order_id": "ORD-001",
        "email": "customer1@example.com",
        "customer_tier": "standard",
        "items": [
            {"sku": "WIDGET-A", "quantity": 1, "unit_price": 10.0},
        ],
        "coupon_code": None,
    },
    {
        "order_id": "ORD-002",
        "email": "customer2@example.com",
        "customer_tier": "silver",
        "items": [
            {"sku": "WIDGET-A", "quantity": 2, "unit_price": 25.0},
            {"sku": "WIDGET-B", "quantity": 1, "unit_price": 50.0},
        ],
        "coupon_code": "DISCOUNT10",
    },
    {
        "order_id": "ORD-003",
        "email": "customer3@example.com",
        "customer_tier": "gold",
        "items": [
            {"sku": "GADGET-X", "quantity": 4, "unit_price": 100.0},
        ],
        "coupon_code": "DISCOUNT20",
    },
]


@pytest.fixture(autouse=True)
def _reset_global_state() -> None:
    """Ensure legacy monolithic before database is clean between tests."""
    before.reset_database()


def _to_comparable_dict(order_record: ProcessedOrder) -> dict[str, Any]:
    """Convert ProcessedOrder dataclass into a comparable dictionary."""
    return {
        "order_id": order_record.order_id,
        "email": order_record.email,
        "customer_tier": order_record.customer_tier,
        "subtotal": order_record.subtotal,
        "discount": order_record.discount,
        "tax": order_record.tax,
        "total": order_record.total,
        "status": order_record.status,
        "notification": order_record.notification,
    }


def _convert_before_to_decimals(before_dict: dict[str, Any]) -> dict[str, Any]:
    """Cast floating-point numeric fields from before.py into exact Decimal equivalents."""
    converted = dict(before_dict)
    for monetary_field in ("subtotal", "discount", "tax", "total"):
        converted[monetary_field] = Decimal(str(before_dict[monetary_field]))
    return converted


@pytest.mark.parametrize("payload", PARAMETRIZED_ORDERS)
def test_differential_parity_between_before_and_after(payload: dict[str, Any]) -> None:
    """Verify that monolithic before.py and modular after package produce equivalent outputs."""
    before_result = before.process_order(payload)
    service = build_order_service()
    after_result = service.process_order(payload)

    assert _to_comparable_dict(after_result) == _convert_before_to_decimals(before_result)


def test_after_facade_service_with_injected_repository() -> None:
    """Verify that fresh service instance operates with its own isolated repository."""
    isolated_repository = OrderRepository()
    service = build_order_service(repository=isolated_repository)

    order_payload = {
        "order_id": "ORD-ISOLATED",
        "email": "test@example.com",
        "customer_tier": "silver",
        "items": [{"sku": "SKU-1", "quantity": 2, "unit_price": 15.0}],
        "coupon_code": "DISCOUNT10",
    }
    result = service.process_order(order_payload)
    expected_values = {
        "order_id": "ORD-ISOLATED",
        "subtotal": Decimal("30.00"),
        "discount": Decimal("11.50"),
        "tax": Decimal("3.89"),  # 21% of (30 - 11.5) = 3.885 -> 3.89 with ROUND_HALF_UP
        "total": Decimal("22.39"),
    }
    actual_values = {
        "order_id": result.order_id,
        "subtotal": result.subtotal,
        "discount": result.discount,
        "tax": result.tax,
        "total": result.total,
    }
    assert actual_values == expected_values
    assert isolated_repository.get("ORD-ISOLATED") == result


def test_decimal_precision_accuracy_in_order_pricing() -> None:
    """Demonstrate that Decimal pricing calculation eliminates binary floating point drift."""
    order_payload = {
        "order_id": "ORD-PRECISION",
        "email": "precision@example.com",
        "customer_tier": "standard",
        "items": [{"sku": "MICRO-1", "quantity": 3, "unit_price": "0.10"}],
        "coupon_code": None,
    }
    service = build_order_service()
    result = service.process_order(order_payload)
    assert result.subtotal == Decimal("0.30")


@pytest.mark.parametrize(
    ("invalid_payload", "expected_exception"),
    [
        ("not a dict", TypeError),
        (
            {
                "order_id": "",
                "email": "a@b.com",
                "items": [{"sku": "A", "quantity": 1, "unit_price": 1.0}],
            },
            ValueError,
        ),
        (
            {
                "order_id": "1",
                "email": "invalid-email",
                "items": [{"sku": "A", "quantity": 1, "unit_price": 1.0}],
            },
            ValueError,
        ),
        (
            {
                "order_id": "1",
                "email": "a@b.com",
                "customer_tier": "unknown",
                "items": [{"sku": "A", "quantity": 1, "unit_price": 1.0}],
            },
            ValueError,
        ),
        ({"order_id": "1", "email": "a@b.com", "items": []}, ValueError),
        (
            {
                "order_id": "1",
                "email": "a@b.com",
                "items": [{"sku": "", "quantity": 1, "unit_price": 1.0}],
            },
            ValueError,
        ),
        (
            {
                "order_id": "1",
                "email": "a@b.com",
                "items": [{"sku": "A", "quantity": 0, "unit_price": 1.0}],
            },
            ValueError,
        ),
        (
            {
                "order_id": "1",
                "email": "a@b.com",
                "items": [{"sku": "A", "quantity": 1, "unit_price": -1.0}],
            },
            ValueError,
        ),
        (
            {
                "order_id": "1",
                "email": "a@b.com",
                "coupon_code": "INVALID",
                "items": [{"sku": "A", "quantity": 1, "unit_price": 1.0}],
            },
            ValueError,
        ),
    ],
)
def test_validation_error_parity(invalid_payload: Any, expected_exception: type[Exception]) -> None:
    """Verify that both implementations reject identical invalid inputs with the same error type."""
    service = build_order_service()
    with pytest.raises(expected_exception):
        before.process_order(invalid_payload)

    with pytest.raises(expected_exception):
        service.process_order(invalid_payload)

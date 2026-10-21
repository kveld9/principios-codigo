"""Tests verifying the Money value object arithmetic, validation, and rounding accuracy."""

from decimal import Decimal

import pytest

from examples.value_object.after import Money
from examples.value_object.before import (
    add_monetary_amounts,
    calculate_tax,
    subtract_monetary_amounts,
)


def test_float_rounding_imprecision_vs_money_value_object() -> None:
    """Float addition suffers from binary floating-point inaccuracy, while Money is exact."""
    # Classical floating-point imprecision demonstration: 0.1 + 0.2 != 0.3
    raw_float_sum = add_monetary_amounts(0.1, 0.2)
    assert raw_float_sum != 0.3
    assert raw_float_sum == 0.30000000000000004

    # Money value object addition maintains exact decimal precision
    money_sum = Money("0.10", "USD") + Money("0.20", "USD")
    assert money_sum == Money("0.30", "USD")


def test_float_subtraction_imprecision_vs_money_value_object() -> None:
    """Float subtraction suffers from binary floating-point inaccuracy, while Money is exact."""
    raw_float_diff = subtract_monetary_amounts(1.03, 0.42)
    assert raw_float_diff != 0.61
    assert raw_float_diff == 0.6100000000000001

    money_diff = Money("1.03", "USD") - Money("0.42", "USD")
    assert money_diff == Money("0.61", "USD")


def test_tax_calculation_rounding_correctness() -> None:
    """Tax calculation with Money rounds halves up to exact cents."""
    # Float tax on 19.99 at 7% produces 1.3993
    float_tax = calculate_tax(19.99, 0.07)
    assert float_tax != 1.40

    money_price = Money("19.99", "USD")
    money_tax = money_price * Decimal("0.07")
    assert money_tax == Money("1.40", "USD")


def test_money_rejects_mixed_currency_arithmetic() -> None:
    """Arithmetic between different currencies raises ValueError."""
    usd_money = Money("50.00", "USD")
    eur_money = Money("50.00", "EUR")

    with pytest.raises(ValueError, match="Cannot add different currencies"):
        _ = usd_money + eur_money

    with pytest.raises(ValueError, match="Cannot subtract different currencies"):
        _ = usd_money - eur_money


@pytest.mark.parametrize(
    ("invalid_amount", "invalid_currency"),
    [
        ("abc", "USD"),
        (None, "USD"),
        ("10.00", "us"),
        ("10.00", "US1"),
        ("10.00", "usd"),
    ],
)
def test_money_construction_validation(
    invalid_amount: object,
    invalid_currency: str,
) -> None:
    """Invalid amount types or invalid ISO currency codes raise appropriate exceptions."""
    with pytest.raises((ValueError, TypeError)):
        Money(invalid_amount, invalid_currency)  # type: ignore[arg-type]


def test_money_penny_exact_splitting() -> None:
    """Splitting an odd amount across parts preserves total without lost or phantom cents."""
    total = Money("100.00", "USD")
    parts = total.split(3)

    assert parts == [
        Money("33.34", "USD"),
        Money("33.33", "USD"),
        Money("33.33", "USD"),
    ]
    assert sum(parts, Money("0.00", "USD")) == total


def test_money_rejects_float_amount() -> None:
    """Money constructor strictly rejects float amounts with TypeError."""
    with pytest.raises(TypeError, match="Float amounts are rejected"):
        Money(10.50, "USD")  # type: ignore[arg-type]


def test_money_rejects_float_multiplication() -> None:
    """Money multiplication strictly rejects float factors with TypeError."""
    price = Money("10.00", "USD")
    with pytest.raises(TypeError, match="Float factors are rejected"):
        _ = price * 1.5  # type: ignore[operator]

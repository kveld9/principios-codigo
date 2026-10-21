"""Differential and edge-case tests comparing before and after guard_clauses."""

from decimal import Decimal
from typing import Any

import pytest

from examples.guard_clauses.after import calculate_shipping_cost as after_calculate
from examples.guard_clauses.before import calculate_shipping_cost as before_calculate

VALID_SCENARIOS: list[dict[str, Any]] = [
    {
        "weight_kg": 2.0,
        "distance_km": 30.0,
        "shipping_type": "standard",
        "is_fragile": False,
        "is_hazardous": False,
    },
    {
        "weight_kg": 15.0,
        "distance_km": 150.0,
        "shipping_type": "standard",
        "is_fragile": True,
        "is_hazardous": False,
    },
    {
        "weight_kg": 5.0,
        "distance_km": 350.0,
        "shipping_type": "express",
        "is_fragile": False,
        "is_hazardous": True,
    },
    {
        "weight_kg": 25.0,
        "distance_km": 40.0,
        "shipping_type": "express",
        "is_fragile": True,
        "is_hazardous": False,
    },
    {
        "weight_kg": 8.0,
        "distance_km": 100.0,
        "shipping_type": "overnight",
        "is_fragile": True,
        "is_hazardous": True,
    },
    {
        "weight_kg": 3.0,
        "distance_km": 25.0,
        "shipping_type": "same_day",
        "is_fragile": False,
        "is_hazardous": False,
    },
    {
        "weight_kg": 10.0,
        "distance_km": 50.0,
        "shipping_type": "standard",
        "is_fragile": False,
        "is_hazardous": False,
    },
    {
        "weight_kg": 10.0,
        "distance_km": 200.0,
        "shipping_type": "standard",
        "is_fragile": False,
        "is_hazardous": False,
    },
]

INVALID_SCENARIOS: list[tuple[dict[str, Any], type[Exception]]] = [
    (
        {
            "weight_kg": 0.0,
            "distance_km": 100.0,
            "shipping_type": "standard",
            "is_fragile": False,
            "is_hazardous": False,
        },
        ValueError,
    ),
    (
        {
            "weight_kg": -5.0,
            "distance_km": 100.0,
            "shipping_type": "standard",
            "is_fragile": False,
            "is_hazardous": False,
        },
        ValueError,
    ),
    (
        {
            "weight_kg": 10.0,
            "distance_km": 0.0,
            "shipping_type": "standard",
            "is_fragile": False,
            "is_hazardous": False,
        },
        ValueError,
    ),
    (
        {
            "weight_kg": 10.0,
            "distance_km": -20.0,
            "shipping_type": "standard",
            "is_fragile": False,
            "is_hazardous": False,
        },
        ValueError,
    ),
    (
        {
            "weight_kg": 10.0,
            "distance_km": 100.0,
            "shipping_type": "drone",
            "is_fragile": False,
            "is_hazardous": False,
        },
        ValueError,
    ),
    (
        {
            "weight_kg": 10.0,
            "distance_km": 100.0,
            "shipping_type": "same_day",
            "is_fragile": False,
            "is_hazardous": True,
        },
        ValueError,
    ),
]


@pytest.mark.parametrize("scenario_parameters", VALID_SCENARIOS)
def test_shipping_cost_parity_on_valid_inputs(scenario_parameters: dict[str, Any]) -> None:
    """Verify that both implementations produce equivalent shipping costs across scenarios."""
    before_cost = before_calculate(**scenario_parameters)
    after_cost = after_calculate(**scenario_parameters)
    expected_decimal_cost = Decimal(str(before_cost))
    assert after_cost == expected_decimal_cost


def test_decimal_precision_accuracy_over_float_drift() -> None:
    """Demonstrate that Decimal calculation remains exact where float arithmetic drifts."""
    # With weight_kg=10.1, excess is 0.1 kg. In float, 0.1 * 1.5 = 0.1500000000000008.
    after_cost = after_calculate(
        weight_kg=10.1,
        distance_km=30.0,
        shipping_type="standard",
    )
    assert after_cost == Decimal("5.15")


@pytest.mark.parametrize(("scenario_parameters", "expected_exception"), INVALID_SCENARIOS)
def test_shipping_cost_parity_on_invalid_inputs(
    scenario_parameters: dict[str, Any],
    expected_exception: type[Exception],
) -> None:
    """Verify that both implementations raise identical exception types on invalid inputs."""
    with pytest.raises(expected_exception):
        before_calculate(**scenario_parameters)

    with pytest.raises(expected_exception):
        after_calculate(**scenario_parameters)

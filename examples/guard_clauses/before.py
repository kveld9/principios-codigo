"""Anti-pattern: Deeply nested conditionals and excessive cyclomatic complexity.

This implementation computes shipping costs using deeply nested if-else structures
instead of guard clauses and dispatch tables, producing an anti-pattern with CC >= 11.
"""


def calculate_shipping_cost(
    weight_kg: float,
    distance_km: float,
    shipping_type: str,
    is_fragile: bool = False,
    is_hazardous: bool = False,
) -> float:
    """Calculate shipping cost using deeply nested conditional logic."""
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    else:
        if distance_km <= 0:
            raise ValueError("Distance must be positive")
        else:
            if is_hazardous and shipping_type == "same_day":
                raise ValueError("Hazardous materials cannot use same day delivery")
            else:
                if shipping_type == "standard":
                    if distance_km < 50:
                        base = 5.0
                    elif distance_km < 200:
                        base = 10.0
                    else:
                        base = 15.0
                    multiplier = 1.0
                elif shipping_type == "express":
                    if distance_km < 50:
                        base = 10.0
                    elif distance_km < 200:
                        base = 20.0
                    else:
                        base = 30.0
                    multiplier = 1.5
                elif shipping_type == "overnight":
                    if distance_km < 50:
                        base = 20.0
                    elif distance_km < 200:
                        base = 40.0
                    else:
                        base = 60.0
                    multiplier = 2.0
                elif shipping_type == "same_day":
                    if distance_km < 50:
                        base = 35.0
                    elif distance_km < 200:
                        base = 70.0
                    else:
                        base = 100.0
                    multiplier = 3.0
                else:
                    raise ValueError(f"Unknown shipping type: {shipping_type}")

                if weight_kg > 10.0:
                    weight_fee = (weight_kg - 10.0) * 1.5
                else:
                    weight_fee = 0.0

                cost = (base + weight_fee) * multiplier

                if is_fragile:
                    cost = cost + 12.0

                if is_hazardous:
                    cost = cost + 25.0

                return round(cost, 2)

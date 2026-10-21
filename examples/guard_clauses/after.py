"""Refactored shipping cost calculation using guard clauses and dispatch tables."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

SHORT_DISTANCE_THRESHOLD_KM: float = 50.0
MEDIUM_DISTANCE_THRESHOLD_KM: float = 200.0


@dataclass(frozen=True)
class ShippingTier:
    """Rate configuration for a specific shipping category."""

    short_distance_base_rate: Decimal
    medium_distance_base_rate: Decimal
    long_distance_base_rate: Decimal
    multiplier: Decimal

    def resolve_base_rate(self, distance_km: float) -> Decimal:
        """Resolve base rate using linear distance threshold guard clauses."""
        if distance_km < SHORT_DISTANCE_THRESHOLD_KM:
            return self.short_distance_base_rate
        if distance_km < MEDIUM_DISTANCE_THRESHOLD_KM:
            return self.medium_distance_base_rate
        return self.long_distance_base_rate


SHIPPING_DISPATCH: dict[str, ShippingTier] = {
    "standard": ShippingTier(Decimal("5.00"), Decimal("10.00"), Decimal("15.00"), Decimal("1.00")),
    "express": ShippingTier(Decimal("10.00"), Decimal("20.00"), Decimal("30.00"), Decimal("1.50")),
    "overnight": ShippingTier(
        Decimal("20.00"), Decimal("40.00"), Decimal("60.00"), Decimal("2.00")
    ),
    "same_day": ShippingTier(
        Decimal("35.00"), Decimal("70.00"), Decimal("100.00"), Decimal("3.00")
    ),
}

FRAGILE_SURCHARGE: Decimal = Decimal("12.00")
HAZARDOUS_SURCHARGE: Decimal = Decimal("25.00")
WEIGHT_THRESHOLD_KG: float = 10.0
WEIGHT_SURCHARGE_RATE: Decimal = Decimal("1.50")


def _validate_dimensions(weight_kg: float, distance_km: float) -> None:
    """Guard against non-positive weight or distance values."""
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    if distance_km <= 0:
        raise ValueError("Distance must be positive")


def _validate_hazardous_delivery(is_hazardous: bool, shipping_type: str) -> None:
    """Guard against prohibited hazardous same-day deliveries."""
    if is_hazardous and shipping_type == "same_day":
        raise ValueError("Hazardous materials cannot use same day delivery")


def _calculate_weight_fee(weight_kg: float) -> Decimal:
    """Calculate excess weight surcharge using an early return."""
    if weight_kg > WEIGHT_THRESHOLD_KG:
        excess_weight = Decimal(str(weight_kg)) - Decimal(str(WEIGHT_THRESHOLD_KG))
        fee = excess_weight * WEIGHT_SURCHARGE_RATE
        return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal("0.00")


def _calculate_surcharges(is_fragile: bool, is_hazardous: bool) -> Decimal:
    """Compute additive safety handling surcharges."""
    surcharge = Decimal("0.00")
    if is_fragile:
        surcharge += FRAGILE_SURCHARGE
    if is_hazardous:
        surcharge += HAZARDOUS_SURCHARGE
    return surcharge


def calculate_shipping_cost(
    weight_kg: float,
    distance_km: float,
    shipping_type: str,
    is_fragile: bool = False,
    is_hazardous: bool = False,
) -> Decimal:
    """Compute final shipping cost with guard clauses and dictionary dispatch."""
    _validate_dimensions(weight_kg, distance_km)
    _validate_hazardous_delivery(is_hazardous, shipping_type)

    shipping_tier = SHIPPING_DISPATCH.get(shipping_type)
    if shipping_tier is None:
        raise ValueError(f"Unknown shipping type: {shipping_type}")

    base_rate = shipping_tier.resolve_base_rate(distance_km)
    weight_fee = _calculate_weight_fee(weight_kg)
    handling_surcharge = _calculate_surcharges(is_fragile, is_hazardous)

    subtotal = (base_rate + weight_fee) * shipping_tier.multiplier
    total = subtotal + handling_surcharge
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

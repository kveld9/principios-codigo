"""Value object: immutable Money entity with validated construction and exact decimal arithmetic."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

ISO_CURRENCY_CODE_LENGTH: int = 3


def _normalize_amount(amount: Decimal | str | int) -> Decimal:
    """Normalize input into a 2-decimal quantized Decimal."""
    if isinstance(amount, float):
        raise TypeError(
            "Float amounts are rejected to prevent precision loss; use Decimal, int, or str"
        )
    if not isinstance(amount, (int, str, Decimal)):
        raise TypeError(f"Unsupported amount type: {type(amount).__name__}")
    try:
        decimal_amount = Decimal(str(amount))
        return decimal_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid monetary amount: {amount}") from error


def _validate_currency(currency: str) -> str:
    """Ensure currency is a valid 3-letter uppercase ISO symbol."""
    if not isinstance(currency, str):
        raise TypeError("Currency must be a string")
    if len(currency) != ISO_CURRENCY_CODE_LENGTH:
        raise ValueError(f"Currency must be {ISO_CURRENCY_CODE_LENGTH} letters, got: {currency}")
    if not currency.isupper() or not currency.isalpha():
        raise ValueError(f"Currency must be uppercase letters, got: {currency}")
    return currency


@dataclass(frozen=True)
class Money:
    """Immutable monetary value object encapsulating exact amount and currency identity."""

    amount: Decimal
    currency: str

    def __init__(self, amount: Decimal | str | int, currency: str) -> None:
        object.__setattr__(self, "amount", _normalize_amount(amount))
        object.__setattr__(self, "currency", _validate_currency(currency))

    def __add__(self, other: object) -> "Money":
        """Add two Money instances ensuring matching currency."""
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: object) -> "Money":
        """Subtract two Money instances ensuring matching currency."""
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal | str) -> "Money":
        """Multiply monetary amount by a scalar factor."""
        if isinstance(factor, float):
            raise TypeError(
                "Float factors are rejected to prevent precision loss; use Decimal, int, or str"
            )
        if not isinstance(factor, (int, Decimal, str)):
            raise TypeError(f"Unsupported multiplication factor type: {type(factor).__name__}")
        try:
            decimal_factor = Decimal(str(factor))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"Invalid multiplication factor: {factor}") from error
        return Money(self.amount * decimal_factor, self.currency)

    def split(self, parts_count: int) -> list["Money"]:
        """Distribute money into equal parts without losing remainder cents."""
        if parts_count <= 0:
            raise ValueError("Parts count must be a positive integer")

        total_cents = int(self.amount * 100)
        base_cents = total_cents // parts_count
        remainder_cents = total_cents % parts_count

        allocated_parts: list[Money] = []
        for index in range(parts_count):
            portion_cents = base_cents + (1 if index < remainder_cents else 0)
            allocated_parts.append(Money(Decimal(portion_cents) / 100, self.currency))
        return allocated_parts

"""Anti-pattern: Primitive obsession using float for monetary values and loose currency handling.

In this anti-pattern, monetary amounts are represented as primitive floating-point numbers.
Binary floating-point arithmetic introduces silent precision loss, rounding errors, and allows
unintentional addition of incompatible currencies because values lack semantic encapsulation.
"""


def add_monetary_amounts(amount_a: float, amount_b: float) -> float:
    """Add two monetary amounts represented as raw floats."""
    return amount_a + amount_b


def subtract_monetary_amounts(amount_a: float, amount_b: float) -> float:
    """Subtract two monetary amounts represented as raw floats."""
    return amount_a - amount_b


def calculate_tax(amount: float, tax_rate: float) -> float:
    """Calculate tax on an amount using raw float multiplication."""
    return amount * tax_rate


def transfer_funds(
    source_balance: float,
    source_currency: str,
    target_amount: float,
    target_currency: str,
) -> float:
    """Deduct funds without verifying currency matching."""
    # Anti-pattern: Silently mixing currencies without validation
    return source_balance - target_amount

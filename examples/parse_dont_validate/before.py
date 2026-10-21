"""Anti-pattern: Defensive re-validation of unstructured dictionaries and swallowed exceptions.

In this anti-pattern, raw dictionaries are passed across layers. Every downstream function
defensively repeats validation checks on dictionary keys, types, and ranges. When errors
occur, exceptions are caught and swallowed, discarding the original stack trace and context.
"""

from typing import Any


def validate_user_payload(data: dict[str, Any]) -> bool:
    """Validate presence and basic types across dictionary fields."""
    try:
        user_id = int(data["user_id"])
        if user_id <= 0:
            return False
        if not isinstance(data["email"], str) or "@" not in data["email"]:
            return False
        age = int(data["age"])
        if age < 18:
            return False
        return data.get("status") in {"active", "pending", "suspended"}
    except Exception:
        # Anti-pattern: swallowing exceptions and losing original failure cause
        return False


def calculate_discount(data: dict[str, Any]) -> float:
    """Calculate user discount, defensively repeating dictionary parsing and validation."""
    try:
        # Repetitive parsing and re-validation
        age = int(data["age"])
        status = data.get("status")
        if status == "active" and age >= 60:
            return 0.20
        return 0.0
    except Exception:
        # Swallows error and returns fallback value
        return 0.0


def process_user_pipeline(data: dict[str, Any]) -> dict[str, Any]:
    """Execute pipeline relying on repeated manual validation and swallowed errors."""
    if not validate_user_payload(data):
        # The specific field failure and root exception are lost
        return {"success": False, "error": "Validation failed"}

    discount = calculate_discount(data)
    return {
        "success": True,
        "user_id": int(data["user_id"]),
        "discount": discount,
    }

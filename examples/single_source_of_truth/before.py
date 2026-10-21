"""Anti-pattern: Duplicated format lists and hardcoded absolute paths.

In this anti-pattern, format definitions and extensions are duplicated across multiple
independent functions. Furthermore, file storage paths are hardcoded to an absolute user home
directory, preventing environment portability and making local testing intrusive and brittle.
"""

import os

# Anti-pattern: Hardcoded absolute path tied to a developer machine
HARDCODED_BASE_DIR = "/home/developer/.config/app"


def get_file_path(filename: str) -> str:
    """Resolve file path using hardcoded absolute directory."""
    return os.path.join("/home/developer/.config/app", filename)


def validate_format(format_name: str) -> bool:
    """Validate format against a hardcoded list copy #1."""
    # Duplicated list of supported formats
    return format_name in ["json", "yaml", "xml", "csv"]


def get_content_type(format_name: str) -> str:
    """Return content type via hardcoded conditional logic copy #2."""
    if format_name == "json":
        return "application/json"
    if format_name == "yaml":
        return "text/yaml"
    if format_name == "xml":
        return "application/xml"
    if format_name == "csv":
        return "text/csv"
    raise ValueError(f"Unknown format: {format_name}")


def list_supported_extensions() -> list[str]:
    """Return supported extensions from hardcoded copy #3."""
    return [".json", ".yaml", ".xml", ".csv"]


def export_data(format_name: str, payload: str) -> str:
    """Export data verifying format against duplicated list copy #4."""
    if format_name not in ["json", "yaml", "xml", "csv"]:
        raise ValueError(f"Unsupported format: {format_name}")

    target_path = os.path.join(HARDCODED_BASE_DIR, f"report.{format_name}")
    return f"Exported to {target_path}"

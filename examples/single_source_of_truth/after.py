"""Single source of truth: unified format enum and environment-independent path resolution."""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

DEFAULT_STORAGE_DIR: Path = Path(".app_storage")
STORAGE_DIR_ENV_VAR: str = "APP_STORAGE_DIR"


@dataclass(frozen=True)
class FormatSpecification:
    """Encapsulates file extension and MIME content-type for a format."""

    extension: str
    content_type: str


class DocumentFormat(Enum):
    """Authoritative single source of truth for supported document formats."""

    JSON = FormatSpecification(".json", "application/json")
    YAML = FormatSpecification(".yaml", "text/yaml")
    XML = FormatSpecification(".xml", "application/xml")
    CSV = FormatSpecification(".csv", "text/csv")

    @property
    def extension(self) -> str:
        """Derive standard file extension from the format specification."""
        return self.value.extension

    @property
    def content_type(self) -> str:
        """Derive standardized MIME content-type string from the format specification."""
        return self.value.content_type


def list_supported_extensions() -> list[str]:
    """Dynamically derive supported extensions from DocumentFormat members."""
    return [document_format.extension for document_format in DocumentFormat]


def get_content_type(document_format: DocumentFormat) -> str:
    """Retrieve content type directly from the single source of truth."""
    return document_format.content_type


def resolve_storage_dir(
    explicit_dir: Path | str | None = None,
    env_var_name: str = STORAGE_DIR_ENV_VAR,
) -> Path:
    """Resolve storage directory with strict precedence: explicit > env > default."""
    if explicit_dir is not None:
        return Path(explicit_dir)
    environment_path = os.environ.get(env_var_name)
    if environment_path:
        return Path(environment_path)
    return DEFAULT_STORAGE_DIR


def save_document(
    data: str,
    filename: str,
    format_type: DocumentFormat,
    base_dir: Path | None = None,
) -> Path:
    """Write document content to resolved path with derived extension."""
    resolved_directory = resolve_storage_dir(base_dir)
    resolved_directory.mkdir(parents=True, exist_ok=True)

    file_path = resolved_directory / f"{filename}{format_type.extension}"
    file_path.write_text(data, encoding="utf-8")
    return file_path


def read_document(
    filename: str,
    format_type: DocumentFormat,
    base_dir: Path | None = None,
) -> str:
    """Read document content from resolved path using derived extension."""
    resolved_directory = resolve_storage_dir(base_dir)
    file_path = resolved_directory / f"{filename}{format_type.extension}"
    return file_path.read_text(encoding="utf-8")

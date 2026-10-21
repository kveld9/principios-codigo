"""Tests verifying single source of truth format derivation and configuration precedence."""

from pathlib import Path

import pytest

from examples.single_source_of_truth.after import (
    DEFAULT_STORAGE_DIR,
    STORAGE_DIR_ENV_VAR,
    DocumentFormat,
    get_content_type,
    list_supported_extensions,
    read_document,
    resolve_storage_dir,
    save_document,
)
from examples.single_source_of_truth.before import (
    export_data as before_export,
)
from examples.single_source_of_truth.before import (
    get_file_path as before_get_path,
)


def test_format_derivation_from_single_enum_source() -> None:
    """Extensions and MIME types are dynamically derived from DocumentFormat members."""
    expected_extensions = [".json", ".yaml", ".xml", ".csv"]
    expected_content_types = {
        DocumentFormat.JSON: "application/json",
        DocumentFormat.XML: "application/xml",
        DocumentFormat.YAML: "text/yaml",
        DocumentFormat.CSV: "text/csv",
    }
    actual_content_types = {
        document_format: get_content_type(document_format) for document_format in DocumentFormat
    }

    assert list_supported_extensions() == expected_extensions
    assert actual_content_types == expected_content_types


def _has_valid_extension(document_format: DocumentFormat) -> bool:
    return isinstance(document_format.extension, str) and document_format.extension.startswith(".")


def _has_valid_content_type(document_format: DocumentFormat) -> bool:
    return isinstance(document_format.content_type, str) and "/" in document_format.content_type


def test_every_format_member_exposes_extension_and_content_type() -> None:
    """Every DocumentFormat member is self-contained with extension and content_type."""
    assert all(
        _has_valid_extension(document_format) and _has_valid_content_type(document_format)
        for document_format in DocumentFormat
    )


def test_configuration_precedence_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Precedence level 1: Fallback to default directory when no env or argument exists."""
    monkeypatch.delenv(STORAGE_DIR_ENV_VAR, raising=False)
    resolved = resolve_storage_dir()
    assert resolved == DEFAULT_STORAGE_DIR


def test_configuration_precedence_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Precedence level 2: Environment variable overrides hardcoded defaults."""
    environment_dir = tmp_path / "env_storage"
    monkeypatch.setenv(STORAGE_DIR_ENV_VAR, str(environment_dir))

    resolved = resolve_storage_dir()
    assert resolved == environment_dir


def test_configuration_precedence_explicit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Precedence level 3: Explicit argument overrides both environment and defaults."""
    environment_dir = tmp_path / "env_storage"
    explicit_dir = tmp_path / "explicit_storage"
    monkeypatch.setenv(STORAGE_DIR_ENV_VAR, str(environment_dir))

    resolved = resolve_storage_dir(explicit_dir=explicit_dir)
    assert resolved == explicit_dir


def test_document_save_and_read_roundtrip(tmp_path: Path) -> None:
    """Documents are written and read using paths derived from enum extensions and base dir."""
    target_dir = tmp_path / "docs"
    content = '{"project": "principios"}'

    saved_path = save_document(
        data=content,
        filename="config",
        format_type=DocumentFormat.JSON,
        base_dir=target_dir,
    )
    assert saved_path == target_dir / "config.json"
    assert saved_path.exists()

    loaded_content = read_document(
        filename="config",
        format_type=DocumentFormat.JSON,
        base_dir=target_dir,
    )
    assert loaded_content == content


def test_before_contains_hardcoded_paths_and_duplicated_lists() -> None:
    """Before anti-pattern hardcodes absolute home path and duplicates format lists."""
    path = before_get_path("report.json")
    assert "/home/developer" in path
    assert before_export("json", "payload") == "Exported to /home/developer/.config/app/report.json"

    with pytest.raises(ValueError, match="Unsupported format"):
        before_export("unsupported", "payload")

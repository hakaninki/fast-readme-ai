"""Tests for core analyzer and scanner modules."""

import os
from pathlib import Path

import pytest

from core.analyzer.file_reader import read_key_files
from core.analyzer.stack_detector import detect_stack
from core.scanner.directory_tree import build_tree

# Path to the sample project used in tests
SAMPLE_PROJECT = str(
    Path(__file__).resolve().parent.parent / "examples" / "sample_project"
)


class TestBuildTree:
    """Tests for core.scanner.directory_tree.build_tree."""

    def test_returns_non_empty_string(self) -> None:
        """build_tree should return a non-empty string for a valid directory."""
        result = build_tree(SAMPLE_PROJECT)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_expected_files(self) -> None:
        """The tree should include known files from the sample project."""
        result = build_tree(SAMPLE_PROJECT)
        assert "app.py" in result

    def test_contains_directories(self) -> None:
        """The tree should include directory entries."""
        result = build_tree(SAMPLE_PROJECT)
        assert "src" in result


class TestDetectStack:
    """Tests for core.analyzer.stack_detector.detect_stack."""

    def test_returns_dict_with_expected_keys(self) -> None:
        """detect_stack should return a dict with all expected category keys."""
        result = detect_stack(SAMPLE_PROJECT)
        assert isinstance(result, dict)
        for key in ("languages", "frameworks", "databases", "tools", "package_managers"):
            assert key in result, f"Missing key: {key}"

    def test_detects_python(self) -> None:
        """Should detect Python from requirements.txt."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "Python" in result["languages"]

    def test_detects_javascript(self) -> None:
        """Should detect JavaScript from package.json."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "JavaScript" in result["languages"]

    def test_detects_fastapi(self) -> None:
        """Should detect FastAPI from requirements.txt."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "FastAPI" in result["frameworks"]

    def test_detects_react(self) -> None:
        """Should detect React from package.json."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "React" in result["frameworks"]

    def test_detects_postgresql(self) -> None:
        """Should detect PostgreSQL from requirements.txt."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "PostgreSQL" in result["databases"]


class TestReadKeyFiles:
    """Tests for core.analyzer.file_reader.read_key_files."""

    def test_returns_list_of_dicts(self) -> None:
        """read_key_files should return a list of dictionaries."""
        result = read_key_files(SAMPLE_PROJECT, max_files=5, max_size_kb=50)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_dicts_have_required_keys(self) -> None:
        """Each dict should have 'path', 'content', and 'language' keys."""
        result = read_key_files(SAMPLE_PROJECT, max_files=5, max_size_kb=50)
        for item in result:
            assert "path" in item
            assert "content" in item
            assert "language" in item

    def test_python_files_use_ast_summary(self) -> None:
        """Python files should be analyzed with AST, not raw content."""
        result = read_key_files(SAMPLE_PROJECT, max_files=5, max_size_kb=50)
        py_files = [f for f in result if f["language"] == "Python"]
        if py_files:
            # AST summaries contain "Classes:" or "Functions:" or "Docstring:"
            content = py_files[0]["content"]
            assert any(
                marker in content
                for marker in ("Classes:", "Functions:", "Docstring:", "(empty module)")
            )

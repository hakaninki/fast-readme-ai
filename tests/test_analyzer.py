"""Tests for the analyzer module.

Tests cover directory tree building, stack detection, and key file reading
using the sample project under ``examples/sample_project/``.
"""

from pathlib import Path

from analyzer.directory_tree import build_tree
from analyzer.file_reader import read_key_files
from analyzer.stack_detector import detect_stack

# Resolve the path to the sample project relative to the repo root
SAMPLE_PROJECT = str(
    (Path(__file__).resolve().parent.parent / "examples" / "sample_project")
)


class TestBuildTree:
    """Tests for ``build_tree()``."""

    def test_returns_non_empty_string(self) -> None:
        """build_tree should return a non-empty tree string."""
        tree = build_tree(SAMPLE_PROJECT)
        assert isinstance(tree, str)
        assert len(tree) > 0

    def test_contains_expected_files(self) -> None:
        """The tree should include known files from the sample project."""
        tree = build_tree(SAMPLE_PROJECT)
        assert "app.py" in tree
        assert "requirements.txt" in tree
        assert "package.json" in tree

    def test_contains_directories(self) -> None:
        """The tree should show the ``src/`` directory."""
        tree = build_tree(SAMPLE_PROJECT)
        assert "src/" in tree


class TestDetectStack:
    """Tests for ``detect_stack()``."""

    def test_returns_dict_with_expected_keys(self) -> None:
        """detect_stack should return a dict with all required keys."""
        result = detect_stack(SAMPLE_PROJECT)
        assert isinstance(result, dict)
        assert "languages" in result
        assert "frameworks" in result
        assert "databases" in result
        assert "tools" in result
        assert "package_managers" in result

    def test_detects_python(self) -> None:
        """Should detect Python from requirements.txt."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "Python" in result["languages"]

    def test_detects_javascript(self) -> None:
        """Should detect JavaScript from package.json."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "JavaScript" in result["languages"]

    def test_detects_fastapi(self) -> None:
        """Should detect FastAPI from requirements.txt contents."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "FastAPI" in result["frameworks"]

    def test_detects_react(self) -> None:
        """Should detect React from package.json dependencies."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "React" in result["frameworks"]

    def test_detects_postgresql(self) -> None:
        """Should detect PostgreSQL from psycopg2 in requirements.txt."""
        result = detect_stack(SAMPLE_PROJECT)
        assert "PostgreSQL" in result["databases"]


class TestReadKeyFiles:
    """Tests for ``read_key_files()``."""

    def test_returns_list_of_dicts(self) -> None:
        """read_key_files should return a list of dicts."""
        result = read_key_files(SAMPLE_PROJECT, max_files=10, max_size_kb=50)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_dicts_have_required_keys(self) -> None:
        """Each dict should have 'path', 'content', and 'language' keys."""
        result = read_key_files(SAMPLE_PROJECT, max_files=10, max_size_kb=50)
        for item in result:
            assert "path" in item
            assert "content" in item
            assert "language" in item

    def test_python_files_use_ast_summary(self) -> None:
        """Python files should contain AST-extracted summaries, not raw code."""
        result = read_key_files(SAMPLE_PROJECT, max_files=10, max_size_kb=50)
        py_files = [f for f in result if f["language"] == "Python"]
        if py_files:
            # AST summary should mention classes or functions
            content = py_files[0]["content"]
            assert "Classes" in content or "Functions" in content or "(empty module)" in content

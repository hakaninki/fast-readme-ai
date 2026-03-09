"""Tests for the CLI tool."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from core.engine import EngineResult

runner = CliRunner()


def test_version_flag() -> None:
    """--version should print the version string and exit cleanly."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "fast-readme-ai" in result.output


def test_generate_no_save() -> None:
    """--no-save should print README to stdout without writing a file."""
    mock_result = EngineResult(
        success=True,
        project_name="sample_project",
        readme_content="# Sample Project\n\nA sample.\n",
        stack={"languages": ["Python"], "frameworks": [], "databases": [],
               "tools": [], "package_managers": ["pip"]},
    )
    with patch("cli.main.generate", return_value=mock_result):
        result = runner.invoke(app, ["examples/sample_project", "--no-save"])
    assert result.exit_code == 0
    assert "Sample Project" in result.output


def test_generate_invalid_path() -> None:
    """Providing a non-existent path should exit with code 1."""
    mock_result = EngineResult(
        success=False,
        error="Path does not exist: /nonexistent/path",
    )
    with patch("cli.main.generate", return_value=mock_result):
        result = runner.invoke(app, ["/nonexistent/path", "--no-save"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_generate_api_error() -> None:
    """A Gemini API failure should show an error with guidance."""
    mock_result = EngineResult(
        success=False,
        error="Gemini API call failed: 401 Unauthorized",
    )
    with patch("cli.main.generate", return_value=mock_result):
        result = runner.invoke(app, [".", "--no-save"])
    assert result.exit_code == 1
    assert "Gemini API" in result.output

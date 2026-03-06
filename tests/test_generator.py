"""Tests for the generator module.

Tests cover prompt building and Mermaid diagram generation using
representative input data.
"""

from generator.mermaid_builder import build_mermaid_diagram
from generator.prompt_builder import build_prompt


SAMPLE_TREE = """sample_project/
├── src/
│   └── app.py
├── requirements.txt
└── package.json"""

SAMPLE_STACK = {
    "languages": ["JavaScript", "Python"],
    "frameworks": ["FastAPI", "React"],
    "databases": ["PostgreSQL"],
    "tools": ["Docker"],
    "package_managers": ["npm", "pip"],
}

SAMPLE_FILES = [
    {
        "path": "src/app.py",
        "content": "Docstring: Sample app\nClasses: ['UserService']\nFunctions: ['calculate_total']",
        "language": "Python",
    },
    {
        "path": "requirements.txt",
        "content": "fastapi>=0.111.0\nuvicorn>=0.29.0",
        "language": "Unknown",
    },
]


class TestBuildPrompt:
    """Tests for ``build_prompt()``."""

    def test_contains_tree(self) -> None:
        """The prompt should include the directory tree."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "sample_project/" in result
        assert "app.py" in result

    def test_contains_stack_info(self) -> None:
        """The prompt should include detected stack information."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "Python" in result
        assert "FastAPI" in result

    def test_contains_project_name(self) -> None:
        """The prompt should reference the project name."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "test-project" in result

    def test_contains_file_content(self) -> None:
        """The prompt should include analyzed file contents."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "UserService" in result

    def test_contains_readme_instructions(self) -> None:
        """The prompt should contain instructions for README sections."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "## Overview" in result
        assert "## Features" in result
        assert "## Tech Stack" in result


class TestBuildMermaidDiagram:
    """Tests for ``build_mermaid_diagram()``."""

    def test_starts_with_mermaid_fence(self) -> None:
        """Output should start with a mermaid code fence."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert result.startswith("```mermaid")

    def test_ends_with_fence(self) -> None:
        """Output should end with a closing code fence."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert result.strip().endswith("```")

    def test_contains_graph_td(self) -> None:
        """Output should use a top-down graph layout."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert "graph TD" in result

    def test_contains_framework_nodes(self) -> None:
        """Diagram should reference detected frameworks."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert "React" in result
        assert "FastAPI" in result

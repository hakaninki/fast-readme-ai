"""Tests for core generator modules."""

from pathlib import Path
from typing import Dict, List

import pytest

from core.generator.mermaid_builder import (
    _sanitize_label,
    build_mermaid_diagram,
    sanitize_mermaid_in_markdown,
)
from core.generator.prompt_builder import build_prompt

# Reusable test fixtures
SAMPLE_TREE = "project/\n├── src/\n│   └── app.py\n└── requirements.txt"
SAMPLE_STACK: Dict[str, List[str]] = {
    "languages": ["Python"],
    "frameworks": ["FastAPI"],
    "databases": ["PostgreSQL"],
    "tools": [],
    "package_managers": ["pip"],
}
SAMPLE_FILES = [
    {"path": "src/app.py", "content": "Functions: [main]", "language": "Python"}
]


class TestBuildPrompt:
    """Tests for core.generator.prompt_builder.build_prompt."""

    def test_contains_tree(self) -> None:
        """Prompt should contain the directory tree."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert SAMPLE_TREE in result

    def test_contains_stack_info(self) -> None:
        """Prompt should mention detected stack items."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "Python" in result
        assert "FastAPI" in result

    def test_contains_project_name(self) -> None:
        """Prompt should contain the project name."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "my-cool-project")
        assert "my-cool-project" in result

    def test_contains_file_content(self) -> None:
        """Prompt should include analyzed file content."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "src/app.py" in result

    def test_contains_readme_instructions(self) -> None:
        """Prompt should contain README generation instructions."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "README.md" in result
        assert "CRITICAL RULES" in result

    def test_contains_mermaid_instructions(self) -> None:
        """Prompt should contain strict Mermaid diagram rules."""
        result = build_prompt(SAMPLE_TREE, SAMPLE_STACK, SAMPLE_FILES, "test-project")
        assert "MERMAID DIAGRAM RULES" in result


class TestBuildMermaidDiagram:
    """Tests for core.generator.mermaid_builder.build_mermaid_diagram."""

    def test_starts_with_mermaid_fence(self) -> None:
        """Output should start with the Mermaid code fence."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert result.startswith("```mermaid")

    def test_ends_with_fence(self) -> None:
        """Output should end with a closing code fence."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert result.strip().endswith("```")

    def test_contains_graph_td(self) -> None:
        """Output should include the graph TD directive."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert "graph TD" in result

    def test_contains_framework_nodes(self) -> None:
        """Output should contain nodes for detected frameworks."""
        result = build_mermaid_diagram(SAMPLE_STACK, "test-project")
        assert "FastAPI" in result

    def test_no_forbidden_chars_in_labels(self) -> None:
        """Node labels should not contain characters forbidden by GitHub Mermaid."""
        stack_with_special = {
            "languages": ["Python"],
            "frameworks": ["FastAPI", "React"],
            "databases": ["PostgreSQL"],
            "tools": ["Docker"],
            "package_managers": ["pip", "npm"],
        }
        result = build_mermaid_diagram(stack_with_special, "test-project")
        # Extract all node labels [...]
        import re
        labels = re.findall(r'\[([^\]]+)\]', result)
        forbidden = set('()/\\"\'&<>|#@')
        for label in labels:
            for char in forbidden:
                assert char not in label, f"Forbidden char '{char}' found in label: {label}"


class TestSanitizeLabel:
    """Tests for core.generator.mermaid_builder._sanitize_label."""

    def test_removes_parentheses(self) -> None:
        """Should remove parentheses."""
        assert _sanitize_label("FastAPI (Python)") == "FastAPI Python"

    def test_removes_slashes(self) -> None:
        """Should remove slashes."""
        assert _sanitize_label("User/Client") == "UserClient"

    def test_collapses_spaces(self) -> None:
        """Should collapse multiple spaces."""
        assert _sanitize_label("API  (  Server  )") == "API Server"

    def test_clean_string_unchanged(self) -> None:
        """Clean strings should pass through unchanged."""
        assert _sanitize_label("FastAPI Backend") == "FastAPI Backend"


class TestSanitizeMermaidInMarkdown:
    """Tests for core.generator.mermaid_builder.sanitize_mermaid_in_markdown."""

    def test_removes_forbidden_chars_from_mermaid_blocks(self) -> None:
        """Should sanitize node labels inside mermaid blocks."""
        content = '```mermaid\ngraph TD\n    A[User/Client (HTTP)] --> B[Server]\n```'
        result = sanitize_mermaid_in_markdown(content)
        assert "(HTTP)" not in result
        assert "/" not in result.split("```mermaid")[1].split("```")[0].replace("-->", "")

    def test_preserves_non_mermaid_content(self) -> None:
        """Should not modify content outside mermaid blocks."""
        content = "# Title\n\nSome text with (parentheses).\n\n```mermaid\ngraph TD\n    A[Clean Node]\n```"
        result = sanitize_mermaid_in_markdown(content)
        assert "(parentheses)" in result

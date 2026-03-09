"""Core engine orchestrator for fast-readme-ai.

Provides the single ``generate()`` function that all interfaces (CLI, API)
call to execute the full README generation pipeline.  This module is
completely interface-agnostic — it never imports from ``cli/`` or ``api/``.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from config import MAX_FILE_SIZE_KB, MAX_FILES_TO_ANALYZE
from core.analyzer.file_reader import read_key_files
from core.analyzer.stack_detector import detect_stack
from core.generator.mermaid_builder import sanitize_mermaid_in_markdown
from core.generator.prompt_builder import build_prompt
from core.generator.readme_writer import write_readme
from core.scanner.directory_tree import build_tree
from core.scanner.repo_cloner import clone_repo
from core.services.gemini_service import generate_readme

logger = logging.getLogger(__name__)

# Regex to extract Mermaid blocks from generated content
MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


@dataclass
class EngineResult:
    """Result of a README generation run.

    Attributes:
        success: Whether the generation completed without errors.
        project_name: The resolved project name.
        readme_content: The full generated README.md content.
        output_path: The file path where the README was saved, if any.
        stack: The detected technology stack dictionary.
        mermaid_diagram: The extracted Mermaid diagram block, if any.
        error: An error message if generation failed, otherwise None.
    """

    success: bool = False
    project_name: str = ""
    readme_content: str = ""
    output_path: Optional[str] = None
    stack: Dict[str, Any] = field(default_factory=dict)
    mermaid_diagram: Optional[str] = None
    error: Optional[str] = None


def _is_github_url(source: str) -> bool:
    """Check whether a source string looks like a GitHub URL.

    Args:
        source: The source string to check.

    Returns:
        True if the source appears to be a GitHub URL, False otherwise.
    """
    return source.startswith("https://github.com/")


def _extract_mermaid(content: str) -> Optional[str]:
    """Extract the first Mermaid diagram block from Markdown content.

    Args:
        content: The full Markdown content string.

    Returns:
        The Mermaid block (including fences) if found, otherwise None.
    """
    match = MERMAID_PATTERN.search(content)
    if match:
        return f"```mermaid\n{match.group(1)}```"
    return None


def generate(
    source: str,
    project_name: Optional[str] = None,
    output_path: Optional[str] = None,
    model: str = "gemini-2.5-flash",
) -> EngineResult:
    """Execute the full README generation pipeline.

    Orchestrates: source resolution → tree building → stack detection →
    file analysis → prompt building → Gemini call → post-processing →
    optional file write.

    This function **never raises exceptions**.  All errors are captured
    and returned inside the ``EngineResult`` with ``success=False``.

    Args:
        source: A local directory path or GitHub HTTPS URL.
        project_name: Optional project name override.  Inferred from the
            directory name if not provided.
        output_path: Optional file path to write the generated README.
        model: Gemini model name to use for generation.

    Returns:
        An ``EngineResult`` containing the generated README and metadata.
    """
    try:
        # Step 1: Resolve source to a local path
        if _is_github_url(source):
            local_path = clone_repo(source)
        else:
            path = Path(source).resolve()
            if not path.exists():
                return EngineResult(
                    success=False,
                    error=f"Path does not exist: {source}",
                )
            if not path.is_dir():
                return EngineResult(
                    success=False,
                    error=f"Path is not a directory: {source}",
                )
            local_path = str(path)

        # Step 2: Analyze the project
        tree = build_tree(local_path)
        stack = detect_stack(local_path)
        files = read_key_files(
            local_path,
            max_files=MAX_FILES_TO_ANALYZE,
            max_size_kb=MAX_FILE_SIZE_KB,
        )

        # Step 3: Resolve project name
        resolved_name = project_name or Path(local_path).name

        # Step 4: Build prompt and call Gemini
        system_instruction, prompt = build_prompt(tree, stack, files, resolved_name)
        readme_content = generate_readme(system_instruction, prompt)

        # Step 5: Sanitize Mermaid diagrams
        readme_content = sanitize_mermaid_in_markdown(readme_content)

        # Step 6: Collapse excessive blank lines
        readme_content = re.sub(r'\n{3,}', '\n\n', readme_content).strip() + "\n"

        # Step 7: Extract Mermaid diagram
        mermaid_diagram = _extract_mermaid(readme_content)

        # Step 8: Optionally write to disk
        saved_path = None
        if output_path:
            saved_path = write_readme(readme_content, output_path)

        return EngineResult(
            success=True,
            project_name=resolved_name,
            readme_content=readme_content,
            output_path=saved_path,
            stack=stack,
            mermaid_diagram=mermaid_diagram,
        )

    except ValueError as exc:
        return EngineResult(success=False, error=str(exc))
    except RuntimeError as exc:
        return EngineResult(success=False, error=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during generation")
        return EngineResult(success=False, error=f"Internal error: {exc}")

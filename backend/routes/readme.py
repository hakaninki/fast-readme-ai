"""API routes for README generation."""

import logging
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException

from analyzer.directory_tree import build_tree
from analyzer.file_reader import read_key_files
from analyzer.repo_cloner import clone_repo
from analyzer.stack_detector import detect_stack
from backend.config import settings
from backend.models.schemas import GenerateRequest, GenerateResponse
from backend.services.gemini_service import generate_readme
from generator.prompt_builder import build_prompt
from generator.readme_writer import write_readme

logger = logging.getLogger(__name__)

router = APIRouter()

# Regex to extract Mermaid blocks from generated content
MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def _is_github_url(source: str) -> bool:
    """Check whether a source string looks like a GitHub URL.

    Args:
        source: The source string to check.

    Returns:
        True if the source appears to be a GitHub URL, False otherwise.
    """
    return source.startswith("https://github.com/")


def _extract_mermaid(content: str) -> str | None:
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


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        A dict with ``status: ok``.
    """
    return {"status": "ok"}


@router.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(request: GenerateRequest) -> GenerateResponse:
    """Generate a README.md from a project source.

    Orchestrates the full pipeline: clone (if GitHub URL), analyze directory
    tree, detect stack, read key files, build prompt, call Gemini, and
    optionally write to disk.

    Args:
        request: The generation request containing source path/URL and options.

    Returns:
        A ``GenerateResponse`` with the generated README and metadata.

    Raises:
        HTTPException: On validation errors, clone failures, or API errors.
    """
    try:
        # Step 1: Resolve source to a local path
        if _is_github_url(request.source):
            try:
                local_path = clone_repo(request.source)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
        else:
            local_path = request.source
            if not Path(local_path).exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Path does not exist: {local_path}",
                )
            if not Path(local_path).is_dir():
                raise HTTPException(
                    status_code=400,
                    detail=f"Path is not a directory: {local_path}",
                )

        # Step 2: Analyze the project
        tree = build_tree(local_path)
        stack = detect_stack(local_path)
        files = read_key_files(
            local_path,
            max_files=settings.MAX_FILES_TO_ANALYZE,
            max_size_kb=settings.MAX_FILE_SIZE_KB,
        )

        # Step 3: Resolve project name
        project_name = request.project_name or Path(local_path).name

        # Step 4: Build prompt and call Gemini
        prompt = build_prompt(tree, stack, files, project_name)

        try:
            readme_content = generate_readme(prompt)
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc))

        # Step 5: Optionally write to disk
        output_path = None
        if request.output_path:
            output_path = write_readme(readme_content, request.output_path)

        # Step 6: Extract Mermaid diagram
        mermaid_diagram = _extract_mermaid(readme_content)

        return GenerateResponse(
            success=True,
            project_name=project_name,
            readme_content=readme_content,
            output_path=output_path,
            stack=stack,
            mermaid_diagram=mermaid_diagram,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during generation")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {exc}",
        )

"""Pydantic v2 request and response models for the README generation API."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    """Request model for the ``POST /generate`` endpoint.

    Attributes:
        source: A local directory path or GitHub HTTPS URL.
        project_name: Optional project name; inferred from directory if omitted.
        output_path: Optional file path to write the README to disk.
        model: Gemini model name to use (defaults to ``gemini-2.5-flash``).
    """

    source: str
    project_name: Optional[str] = None
    output_path: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"


class GenerateResponse(BaseModel):
    """Response model for the ``POST /generate`` endpoint.

    Attributes:
        success: Whether the generation completed successfully.
        project_name: The resolved project name.
        readme_content: The full generated README.md content.
        output_path: The file path where the README was saved, if applicable.
        stack: The detected technology stack dictionary.
        mermaid_diagram: The extracted Mermaid diagram block, if present.
        error: Error message if generation failed.
    """

    success: bool
    project_name: str
    readme_content: str
    output_path: Optional[str] = None
    stack: Dict[str, Any] = {}
    mermaid_diagram: Optional[str] = None
    error: Optional[str] = None

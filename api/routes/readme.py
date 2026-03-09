"""API route for README generation.

This is a thin wrapper that delegates all logic to ``core.engine.generate()``.
No analyzer or generator logic belongs in this file.
"""

import logging

from fastapi import APIRouter, HTTPException

from core.engine import generate
from core.models.schemas import GenerateRequest, GenerateResponse

logger = logging.getLogger(__name__)

router = APIRouter()


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

    Delegates the entire pipeline to the core engine and maps the result
    to the API response model.

    Args:
        request: The generation request containing source path/URL and options.

    Returns:
        A ``GenerateResponse`` with the generated README and metadata.

    Raises:
        HTTPException: On generation failures.
    """
    result = generate(
        source=request.source,
        project_name=request.project_name,
        output_path=request.output_path,
        model=request.model or "gemini-2.5-flash",
    )

    if not result.success:
        # Determine appropriate HTTP status code
        error_msg = result.error or "Unknown error"
        if "not exist" in error_msg or "not a directory" in error_msg:
            status_code = 400
        elif "clone" in error_msg.lower() or "github" in error_msg.lower():
            status_code = 400
        elif "Gemini API" in error_msg:
            status_code = 502
        else:
            status_code = 500
        raise HTTPException(status_code=status_code, detail=error_msg)

    return GenerateResponse(
        success=result.success,
        project_name=result.project_name,
        readme_content=result.readme_content,
        output_path=result.output_path,
        stack=result.stack,
        mermaid_diagram=result.mermaid_diagram,
        error=result.error,
    )

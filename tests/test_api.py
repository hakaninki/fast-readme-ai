"""Tests for the FastAPI application endpoints."""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app
from core.engine import EngineResult


@pytest.fixture
def mock_engine_result() -> EngineResult:
    """Create a mock EngineResult for testing.

    Returns:
        An EngineResult with sample data.
    """
    return EngineResult(
        success=True,
        project_name="test-project",
        readme_content="# Test Project\n\nA test project.\n",
        output_path=None,
        stack={"languages": ["Python"], "frameworks": ["FastAPI"],
               "databases": [], "tools": [], "package_managers": ["pip"]},
        mermaid_diagram="```mermaid\ngraph TD\n    A[Client] --> B[Server]\n```",
    )


@pytest.mark.asyncio
async def test_health_check() -> None:
    """GET /health should return status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """GET / should return tool info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["tool"] == "fast-readme-ai"
    assert "version" in data


@pytest.mark.asyncio
async def test_generate_with_local_path(mock_engine_result: EngineResult) -> None:
    """POST /generate with a valid local path should return a README."""
    with patch("api.routes.readme.generate", return_value=mock_engine_result):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/generate",
                json={"source": "/some/path", "project_name": "test-project"},
            )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "readme_content" in data
    assert data["project_name"] == "test-project"


@pytest.mark.asyncio
async def test_generate_with_invalid_path() -> None:
    """POST /generate with a non-existent path should return an error."""
    result = EngineResult(success=False, error="Path does not exist: /nonexistent")
    with patch("api.routes.readme.generate", return_value=result):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/generate",
                json={"source": "/nonexistent"},
            )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_generate_extracts_mermaid(mock_engine_result: EngineResult) -> None:
    """POST /generate should include the mermaid_diagram in the response."""
    with patch("api.routes.readme.generate", return_value=mock_engine_result):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/generate",
                json={"source": "/some/path"},
            )
    data = response.json()
    assert data["mermaid_diagram"] is not None
    assert "mermaid" in data["mermaid_diagram"]

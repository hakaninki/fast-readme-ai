"""Tests for the FastAPI API endpoints.

Uses ``httpx.AsyncClient`` with the FastAPI app and mocks the Gemini
service to avoid real API calls.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app

SAMPLE_PROJECT = str(
    (Path(__file__).resolve().parent.parent / "examples" / "sample_project")
)

MOCK_README = """# Sample Project

## Overview

This is a sample project for testing.

## Features

- Feature 1
- Feature 2

```mermaid
graph TD
    A[Client] --> B[Server]
```
"""


@pytest.fixture
def anyio_backend():
    """Configure pytest-asyncio to use asyncio."""
    return "asyncio"


@pytest.mark.asyncio
async def test_health_check() -> None:
    """GET /health should return 200 with status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """GET / should return tool name and version."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "fast-readme-ai"
    assert "version" in data


@pytest.mark.asyncio
async def test_generate_with_local_path() -> None:
    """POST /generate with a valid local path should return a README."""
    with patch(
        "backend.routes.readme.generate_readme",
        return_value=MOCK_README,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/generate",
                json={
                    "source": SAMPLE_PROJECT,
                    "project_name": "sample_project",
                },
            )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["project_name"] == "sample_project"
    assert "readme_content" in data
    assert len(data["readme_content"]) > 0


@pytest.mark.asyncio
async def test_generate_with_invalid_path() -> None:
    """POST /generate with a non-existent path should return 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/generate",
            json={
                "source": "/nonexistent/path/that/does/not/exist",
            },
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_generate_extracts_mermaid() -> None:
    """POST /generate should extract Mermaid diagrams from the output."""
    with patch(
        "backend.routes.readme.generate_readme",
        return_value=MOCK_README,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/generate",
                json={
                    "source": SAMPLE_PROJECT,
                    "project_name": "sample_project",
                },
            )
    data = response.json()
    assert data["mermaid_diagram"] is not None
    assert "graph TD" in data["mermaid_diagram"]

"""FastAPI application for fast-readme-ai.

Provides a REST API that wraps the core engine for integration use cases.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.readme import router

app = FastAPI(
    title="fast-readme-ai",
    description="AI-powered README generator for developers",
    version="1.0.0",
)

# Allow all origins for development / demo use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root() -> dict:
    """Return tool name and version.

    Returns:
        A dict with tool name and version string.
    """
    return {"tool": "fast-readme-ai", "version": "1.0.0"}

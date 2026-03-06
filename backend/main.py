"""FastAPI application entry point for fast-readme-ai.

Configures CORS, includes API routers, and exposes a root endpoint
with tool name and version information.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.readme import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="fast-readme-ai",
    description="AI-powered README.md generator",
    version="1.0.0",
)

# CORS: allow all origins for demo use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root() -> dict:
    """Root endpoint returning tool name and version.

    Returns:
        A dict with ``name`` and ``version`` keys.
    """
    return {
        "name": "fast-readme-ai",
        "version": "1.0.0",
    }

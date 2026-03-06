"""Centralized configuration loader for the fast-readme-ai application.

Loads all environment variables from a ``.env`` file using ``python-dotenv``
and exposes them as a single ``settings`` object.  All other modules must
import configuration values from this module — never call ``os.getenv()``
directly elsewhere.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file from the project root (two levels up from this file)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class _Settings:
    """Application settings populated from environment variables."""

    @property
    def GEMINI_API_KEY(self) -> str:
        """Google Gemini API key."""
        return os.environ.get("GEMINI_API_KEY", "")

    @property
    def GEMINI_MODEL(self) -> str:
        """Gemini model name to use for generation."""
        return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    @property
    def MAX_FILE_SIZE_KB(self) -> int:
        """Maximum file size in KB to read during analysis."""
        return int(os.environ.get("MAX_FILE_SIZE_KB", "50"))

    @property
    def MAX_FILES_TO_ANALYZE(self) -> int:
        """Maximum number of files to analyze."""
        return int(os.environ.get("MAX_FILES_TO_ANALYZE", "20"))

    @property
    def TEMP_DIR(self) -> str:
        """Base temporary directory for cloned repositories."""
        return os.environ.get("TEMP_DIR", "/tmp/fast-readme-ai")


settings = _Settings()

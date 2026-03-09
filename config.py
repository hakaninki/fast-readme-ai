"""Centralized configuration loader for the fast-readme-ai application.

Loads all environment variables from a ``.env`` file using ``python-dotenv``
and exposes them as module-level constants.  All other modules must import
configuration values from this module — never call ``os.getenv()`` directly
elsewhere.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from the project root (same directory as this file)
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_FILE_SIZE_KB: int = int(os.getenv("MAX_FILE_SIZE_KB", "50"))
MAX_FILES_TO_ANALYZE: int = int(os.getenv("MAX_FILES_TO_ANALYZE", "20"))
TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/fast-readme-ai")

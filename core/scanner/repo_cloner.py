"""Clones a GitHub repository to a local temporary directory."""

import logging
import re
import subprocess
import uuid
from pathlib import Path

from config import TEMP_DIR

logger = logging.getLogger(__name__)

# Pattern to match valid GitHub HTTPS URLs
GITHUB_URL_PATTERN = re.compile(
    r"^https://github\.com/[\w.\-]+/[\w.\-]+(\.git)?/?$"
)


def clone_repo(github_url: str) -> str:
    """Clone a GitHub repository to a local temporary directory.

    Validates that the URL is a proper GitHub HTTPS URL, then uses
    ``git clone`` to download the repository into a unique subdirectory
    under the configured temp directory.

    Args:
        github_url: The HTTPS URL of the GitHub repository to clone.

    Returns:
        The absolute path to the cloned repository on disk.

    Raises:
        ValueError: If the URL is not a valid GitHub HTTPS URL or if
            the ``git clone`` command fails.
    """
    if not GITHUB_URL_PATTERN.match(github_url):
        raise ValueError(
            f"Invalid GitHub URL: {github_url}. "
            "Expected format: https://github.com/owner/repo"
        )

    temp_base = Path(TEMP_DIR)
    temp_base.mkdir(parents=True, exist_ok=True)

    clone_dir = temp_base / str(uuid.uuid4())
    logger.info("Cloning %s into %s", github_url, clone_dir)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", github_url, str(clone_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError(
            f"Failed to clone repository: {exc.stderr.strip()}"
        ) from exc
    except FileNotFoundError:
        raise ValueError(
            "git is not installed or not found in PATH. "
            "Please install git to clone repositories."
        )

    logger.info("Successfully cloned repository to %s", clone_dir)
    return str(clone_dir)

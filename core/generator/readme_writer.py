"""Writes generated README content to disk."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def write_readme(content: str, output_path: str) -> str:
    """Write README content to a file on disk.

    Creates any necessary parent directories before writing.  Returns the
    absolute path of the written file.

    Args:
        content: The full README markdown content string.
        output_path: The desired file path for the README.

    Returns:
        The absolute path of the written file as a string.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(content, encoding="utf-8")
    absolute = str(path.resolve())

    logger.info("README written to: %s", absolute)
    return absolute

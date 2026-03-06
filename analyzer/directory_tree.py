"""Builds a directory tree string representation from a project path.

Generates a formatted string similar to the Unix `tree` command output,
showing the hierarchical structure of files and directories.
"""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# Directories to always skip when building the tree
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache",
}

# Hidden files/dirs that should NOT be skipped
ALLOWED_HIDDEN = {".env.example", ".gitignore"}


def _should_skip(path: Path) -> bool:
    """Determine whether a file or directory should be skipped.

    Args:
        path: The path to evaluate.

    Returns:
        True if the path should be skipped, False otherwise.
    """
    name = path.name

    if name in SKIP_DIRS:
        return True

    # Skip hidden files/dirs unless in the allow-list
    if name.startswith(".") and name not in ALLOWED_HIDDEN:
        return True

    return False


def _build_tree_lines(
    directory: Path,
    prefix: str = "",
    is_root: bool = True,
) -> List[str]:
    """Recursively build tree lines for a directory.

    Args:
        directory: The directory to walk.
        prefix: The current line prefix for indentation.
        is_root: Whether this is the root call.

    Returns:
        A list of formatted tree-line strings.
    """
    lines: List[str] = []

    if is_root:
        lines.append(f"{directory.name}/")

    # Gather and sort children, filtering out skipped entries
    children = sorted(
        [child for child in directory.iterdir() if not _should_skip(child)],
        key=lambda p: (p.is_file(), p.name.lower()),
    )

    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        if child.is_dir():
            lines.append(f"{prefix}{connector}{child.name}/")
            lines.extend(
                _build_tree_lines(child, prefix=prefix + extension, is_root=False)
            )
        else:
            lines.append(f"{prefix}{connector}{child.name}")

    return lines


def build_tree(root_path: str) -> str:
    """Build a directory tree string from the given root path.

    Recursively walks the project directory and returns a formatted string
    that visually represents the file hierarchy, similar to the Unix ``tree``
    command.  Certain directories (e.g. ``.git``, ``node_modules``) and
    hidden files are automatically skipped.

    Args:
        root_path: Absolute path to the project root directory.

    Returns:
        A multi-line string representing the directory tree.

    Raises:
        ValueError: If the provided path does not exist or is not a directory.
    """
    root = Path(root_path)

    if not root.exists():
        raise ValueError(f"Path does not exist: {root_path}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root_path}")

    logger.info("Building directory tree for: %s", root_path)
    lines = _build_tree_lines(root)
    return "\n".join(lines)

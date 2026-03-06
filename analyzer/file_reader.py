"""Reads and analyzes key source files from a project directory.

For Python files, extracts structural summaries using the ``ast`` module.
For all other supported files, returns raw content truncated to a size limit.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# File extensions considered as source code
SOURCE_EXTENSIONS = {".py", ".ts", ".js", ".go", ".rs", ".tsx", ".jsx"}

# Binary / media extensions to always skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".pyc", ".pyo", ".class",
}

# Entry-point files (highest priority)
ENTRY_POINTS = {
    "main.py", "app.py", "index.js", "index.ts", "server.js", "server.ts",
}

# Config files (second priority)
CONFIG_FILES = {
    "package.json", "pyproject.toml", "requirements.txt",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
}

# Directories whose contents are high priority
PRIORITY_DIRS = {"src", "app", "lib", "core"}

# Language mapping by extension
EXTENSION_LANGUAGE = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".json": "JSON",
    ".toml": "TOML",
    ".yml": "YAML",
    ".yaml": "YAML",
}


def _extract_python_summary(source: str) -> str:
    """Extract a structural summary from Python source code using AST.

    Args:
        source: The raw Python source code string.

    Returns:
        A summary string containing docstring, class names, and function names.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source[:500]

    # Module docstring
    docstring = ast.get_docstring(tree) or ""

    classes: List[str] = []
    functions: List[str] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            functions.append(node.name)

    parts: List[str] = []
    if docstring:
        parts.append(f"Docstring: {docstring}")
    if classes:
        parts.append(f"Classes: {classes}")
    if functions:
        parts.append(f"Functions: {functions}")

    return "\n".join(parts) if parts else "(empty module)"


def _file_priority(path: Path, root: Path) -> int:
    """Return a sort-priority for a file (lower = higher priority).

    Args:
        path: The file path.
        root: The project root path.

    Returns:
        An integer priority value.
    """
    if path.name in ENTRY_POINTS:
        return 0
    if path.name in CONFIG_FILES:
        return 1

    try:
        relative = path.relative_to(root)
        if any(part in PRIORITY_DIRS for part in relative.parts):
            return 2
    except ValueError:
        pass

    if path.suffix in SOURCE_EXTENSIONS:
        return 3

    return 4


def _detect_language(path: Path) -> str:
    """Detect the language of a file from its extension.

    Args:
        path: The file path.

    Returns:
        A human-readable language name string.
    """
    return EXTENSION_LANGUAGE.get(path.suffix, "Unknown")


def read_key_files(
    root_path: str,
    max_files: int,
    max_size_kb: int,
) -> List[Dict[str, str]]:
    """Read and analyze key source files from a project directory.

    Files are selected by priority order: entry points first, then config
    files, then source files in priority directories, then remaining source
    files.  Python files are analyzed using the ``ast`` module and only a
    structural summary is returned.  All other files return raw content
    truncated to ``max_size_kb``.

    Args:
        root_path: Absolute path to the project root directory.
        max_files: Maximum number of files to include.
        max_size_kb: Maximum file size in kilobytes to read.

    Returns:
        A list of dicts, each with keys ``path`` (relative), ``content``
        (string), and ``language``.
    """
    root = Path(root_path)
    logger.info("Reading key files from: %s (max=%d, max_size=%dKB)", root_path, max_files, max_size_kb)

    max_size_bytes = max_size_kb * 1024
    candidates: List[Path] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in BINARY_EXTENSIONS:
            continue
        # Skip hidden files
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        # Skip known noise directories
        skip_dirs = {"node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
        if any(part in skip_dirs for part in path.relative_to(root).parts):
            continue
        # Skip files that are too large
        try:
            if path.stat().st_size > max_size_bytes:
                continue
        except OSError:
            continue

        candidates.append(path)

    # Sort by priority
    candidates.sort(key=lambda p: (_file_priority(p, root), p.name.lower()))

    # Take the top N
    selected = candidates[:max_files]
    result: List[Dict[str, str]] = []

    for file_path in selected:
        relative = str(file_path.relative_to(root)).replace("\\", "/")
        language = _detect_language(file_path)

        try:
            raw = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if file_path.suffix == ".py":
            content = _extract_python_summary(raw)
        else:
            content = raw[:max_size_bytes]

        result.append({
            "path": relative,
            "content": content,
            "language": language,
        })

    logger.info("Selected %d key files for analysis", len(result))
    return result

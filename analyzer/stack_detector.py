"""Detects the technology stack of a project by analyzing file extensions,
configuration files, and dependency manifests.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


def _read_text_safe(file_path: Path) -> str:
    """Read a text file safely, returning empty string on failure.

    Args:
        file_path: Path to the file to read.

    Returns:
        The file contents as a string, or empty string on error.
    """
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _check_requirements(content: str, frameworks: Set[str], databases: Set[str]) -> None:
    """Check a requirements.txt-style file for known framework/database packages.

    Args:
        content: The raw text content of the requirements file.
        frameworks: Mutable set to add detected frameworks to.
        databases: Mutable set to add detected databases to.
    """
    lower = content.lower()

    framework_map = {
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "sqlalchemy": "SQLAlchemy",
    }
    for package, name in framework_map.items():
        if package in lower:
            frameworks.add(name)

    db_map = {
        "psycopg2": "PostgreSQL",
        "asyncpg": "PostgreSQL",
        "pymongo": "MongoDB",
        "redis": "Redis",
    }
    for package, name in db_map.items():
        if package in lower:
            databases.add(name)


def _check_package_json(file_path: Path, frameworks: Set[str]) -> None:
    """Check a package.json file for known JavaScript/TypeScript frameworks.

    Args:
        file_path: Path to the package.json file.
        frameworks: Mutable set to add detected frameworks to.
    """
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    all_deps: Dict[str, str] = {}
    all_deps.update(data.get("dependencies", {}))
    all_deps.update(data.get("devDependencies", {}))

    js_framework_map = {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue.js",
        "express": "Express.js",
    }
    for package, name in js_framework_map.items():
        if package in all_deps:
            frameworks.add(name)


def detect_stack(root_path: str) -> Dict[str, List[str]]:
    """Detect the technology stack of a project.

    Walks the project directory and inspects file names, extensions, and the
    contents of configuration / dependency files to determine languages,
    frameworks, databases, tools, and package managers in use.

    Args:
        root_path: Absolute path to the project root directory.

    Returns:
        A dictionary with keys ``languages``, ``frameworks``, ``databases``,
        ``tools``, and ``package_managers``, each mapping to a sorted list
        of detected items.
    """
    root = Path(root_path)
    logger.info("Detecting tech stack for: %s", root_path)

    languages: Set[str] = set()
    frameworks: Set[str] = set()
    databases: Set[str] = set()
    tools: Set[str] = set()
    package_managers: Set[str] = set()

    for path in root.rglob("*"):
        name = path.name

        # --- Language / package-manager detection from file names ---
        if name in ("requirements.txt", "pyproject.toml", "setup.py"):
            languages.add("Python")
            package_managers.add("pip")
            if name == "requirements.txt":
                _check_requirements(_read_text_safe(path), frameworks, databases)
            if name == "pyproject.toml":
                content = _read_text_safe(path)
                _check_requirements(content, frameworks, databases)

        if name == "package.json":
            languages.add("JavaScript")
            package_managers.add("npm")
            _check_package_json(path, frameworks)

        if name == "pnpm-lock.yaml":
            package_managers.add("pnpm")

        if name == "yarn.lock":
            package_managers.add("yarn")

        if name == "Gemfile":
            languages.add("Ruby")

        if name == "go.mod":
            languages.add("Go")

        if name == "Cargo.toml":
            languages.add("Rust")

        if name in ("pom.xml", "build.gradle"):
            languages.add("Java")

        # --- Tool detection ---
        if name in ("Dockerfile", "docker-compose.yml", "docker-compose.yaml"):
            tools.add("Docker")

        if path.is_dir() and name == "workflows" and path.parent.name == ".github":
            tools.add("GitHub Actions")

        # --- Database detection from file extensions ---
        if path.is_file() and path.suffix == ".sql":
            databases.add("SQL/Database")

        # --- Prisma ORM ---
        if path.is_dir() and name == "prisma":
            frameworks.add("Prisma ORM")

        # --- TypeScript detection ---
        if path.is_file() and path.suffix in (".ts", ".tsx"):
            languages.add("TypeScript")

    return {
        "languages": sorted(languages),
        "frameworks": sorted(frameworks),
        "databases": sorted(databases),
        "tools": sorted(tools),
        "package_managers": sorted(package_managers),
    }

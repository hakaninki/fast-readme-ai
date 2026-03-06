"""Generates Mermaid.js architecture diagrams from detected stack information."""

import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

# Mapping of framework names to their architectural role
FRONTEND_FRAMEWORKS = {"React", "Vue.js", "Next.js"}
API_FRAMEWORKS = {"FastAPI", "Django", "Flask", "Express.js"}
DATABASE_NAMES = {"PostgreSQL", "MongoDB", "Redis", "SQL/Database", "SQLAlchemy", "Prisma ORM"}
CONTAINER_TOOLS = {"Docker"}


def _sanitize_label(label: str) -> str:
    """Remove characters that break Mermaid node label parsing on GitHub.

    GitHub's Mermaid renderer rejects parentheses, slashes, and other special
    characters inside node ``[]`` brackets, interpreting them as shape syntax
    tokens.

    Args:
        label: Raw label string to sanitize.

    Returns:
        Sanitized label safe for use inside Mermaid ``[]`` node syntax.
    """
    # Remove all characters forbidden inside Mermaid [] node labels
    label = re.sub(r'[()\/\\\"\',&<>|#@]', '', label)
    # Collapse multiple spaces left behind by removals
    label = re.sub(r'\s+', ' ', label).strip()
    return label


def build_mermaid_diagram(stack: Dict[str, List[str]], project_name: str) -> str:
    """Generate a Mermaid.js ``graph TD`` diagram from the detected stack.

    Maps known framework and tool names to logical architecture nodes
    (Client, API Server, Database, Docker Container) and connects them
    in a top-down flowchart.  All node labels are sanitized to remove
    characters that break GitHub's Mermaid renderer.

    Args:
        stack: A dictionary with keys ``languages``, ``frameworks``,
            ``databases``, ``tools``, ``package_managers``.
        project_name: The name of the project (used in the diagram title).

    Returns:
        A Mermaid code block string ready to embed in Markdown.
    """
    logger.info("Building Mermaid diagram for project: %s", project_name)

    frameworks = set(stack.get("frameworks", []))
    databases = set(stack.get("databases", []))
    tools = set(stack.get("tools", []))

    nodes: List[str] = []
    edges: List[str] = []
    node_id = 0

    def next_id() -> str:
        """Generate the next node identifier."""
        nonlocal node_id
        current = chr(ord("A") + node_id)
        node_id += 1
        return current

    # --- Client / Frontend ---
    frontend = frameworks & FRONTEND_FRAMEWORKS
    if frontend:
        fid = next_id()
        label = _sanitize_label(" ".join(sorted(frontend)) + " Client")
        nodes.append(f"    {fid}[{label}]")
    else:
        fid = next_id()
        nodes.append(f"    {fid}[User Client]")
    client_id = fid

    # --- API Server ---
    api = frameworks & API_FRAMEWORKS
    if api:
        aid = next_id()
        label = _sanitize_label(" ".join(sorted(api)) + " API Server")
        nodes.append(f"    {aid}[{label}]")
    else:
        aid = next_id()
        nodes.append(f"    {aid}[Application Server]")
    api_id = aid
    edges.append(f"    {client_id} --> {api_id}")

    # --- Database ---
    db_matches = databases - {"SQLAlchemy", "Prisma ORM"}
    orm_matches = databases & {"SQLAlchemy", "Prisma ORM"}

    if db_matches:
        did = next_id()
        label = _sanitize_label(" ".join(sorted(db_matches)) + " Database")
        nodes.append(f"    {did}[{label}]")
        edges.append(f"    {api_id} --> {did}")

    if orm_matches:
        oid = next_id()
        label = _sanitize_label(" ".join(sorted(orm_matches)))
        nodes.append(f"    {oid}[{label}]")
        edges.append(f"    {api_id} --> {oid}")
        if db_matches:
            edges.append(f"    {oid} --> {did}")

    # --- Docker ---
    if CONTAINER_TOOLS & tools:
        cid = next_id()
        nodes.append(f"    {cid}[Docker Container]")
        edges.append(f"    {cid} -.- {api_id}")

    # Build the final block
    diagram_lines = ["```mermaid", "graph TD"]
    diagram_lines.extend(nodes)
    diagram_lines.extend(edges)
    diagram_lines.append("```")

    return "\n".join(diagram_lines)


def sanitize_mermaid_in_markdown(content: str) -> str:
    """Find all mermaid code blocks in a markdown string and sanitize node labels.

    Runs as a post-processing safety net on Gemini output to catch any
    forbidden characters in Mermaid node labels that slipped through the
    prompt instructions.

    Args:
        content: Full README markdown string potentially containing mermaid blocks.

    Returns:
        Markdown string with all mermaid ``[]`` node labels sanitized.
    """
    def fix_block(match: re.Match) -> str:
        """Sanitize all node labels within a single mermaid block."""
        block = match.group(1)

        def fix_label(m: re.Match) -> str:
            return f"[{_sanitize_label(m.group(1))}]"

        block = re.sub(r'\[([^\]]+)\]', fix_label, block)
        return f"```mermaid\n{block}\n```"

    return re.sub(
        r'```mermaid\n(.*?)\n```',
        fix_block,
        content,
        flags=re.DOTALL,
    )

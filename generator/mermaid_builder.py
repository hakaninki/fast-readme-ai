"""Generates Mermaid.js architecture diagrams from detected stack information."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Mapping of framework names to their architectural role
FRONTEND_FRAMEWORKS = {"React", "Vue.js", "Next.js"}
API_FRAMEWORKS = {"FastAPI", "Django", "Flask", "Express.js"}
DATABASE_NAMES = {"PostgreSQL", "MongoDB", "Redis", "SQL/Database", "SQLAlchemy", "Prisma ORM"}
CONTAINER_TOOLS = {"Docker"}


def build_mermaid_diagram(stack: Dict[str, List[str]], project_name: str) -> str:
    """Generate a Mermaid.js ``graph TD`` diagram from the detected stack.

    Maps known framework and tool names to logical architecture nodes
    (Client, API Server, Database, Docker Container) and connects them
    in a top-down flowchart.

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
        label = " / ".join(sorted(frontend))
        nodes.append(f'    {fid}["Client ({label})"]')
    else:
        fid = next_id()
        nodes.append(f'    {fid}["Client / User"]')
    client_id = fid

    # --- API Server ---
    api = frameworks & API_FRAMEWORKS
    if api:
        aid = next_id()
        label = " / ".join(sorted(api))
        nodes.append(f'    {aid}["{label} API Server"]')
    else:
        aid = next_id()
        nodes.append(f'    {aid}["Application Server"]')
    api_id = aid
    edges.append(f"    {client_id} --> {api_id}")

    # --- Database ---
    db_matches = databases - {"SQLAlchemy", "Prisma ORM"}
    orm_matches = databases & {"SQLAlchemy", "Prisma ORM"}

    if db_matches:
        did = next_id()
        label = " / ".join(sorted(db_matches))
        nodes.append(f'    {did}[("{label}")]')
        edges.append(f"    {api_id} --> {did}")

    if orm_matches:
        oid = next_id()
        label = " / ".join(sorted(orm_matches))
        nodes.append(f'    {oid}["{label}"]')
        edges.append(f"    {api_id} --> {oid}")
        if db_matches:
            edges.append(f"    {oid} --> {did}")

    # --- Docker ---
    if CONTAINER_TOOLS & tools:
        cid = next_id()
        nodes.append(f'    {cid}["Docker Container"]')
        edges.append(f"    {cid} -.- {api_id}")

    # Build the final block
    diagram_lines = ["```mermaid", "graph TD"]
    diagram_lines.extend(nodes)
    diagram_lines.extend(edges)
    diagram_lines.append("```")

    return "\n".join(diagram_lines)

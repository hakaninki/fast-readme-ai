"""Assembles the complete prompt to send to the Gemini API for README generation."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Strict Mermaid instructions appended to the prompt to prevent
# GitHub parse errors caused by forbidden characters in node labels.
MERMAID_INSTRUCTION = """
## Architecture section rules:

Generate a Mermaid diagram using `graph TD` syntax. Follow these rules exactly:

MERMAID DIAGRAM RULES — mandatory, no exceptions:
1. Node labels inside [] must contain ONLY plain words and spaces. Nothing else.
2. NEVER use these characters inside []: ( ) / \\ " ' , & < > | # @
3. WRONG: A[User/Client (Streamlit/HTTP)]  →  CORRECT: A[User Client]
4. WRONG: B[FastAPI Backend (Python 3.11)]  →  CORRECT: B[FastAPI Backend]
5. WRONG: DB[(PostgreSQL Database)]        →  CORRECT: DB[PostgreSQL Database]
6. Node IDs must be single words with no spaces: A, B, MyNode — never "My Node".
7. Keep labels short: 1 to 4 words maximum.
8. Use plain [] rectangles for ALL nodes. Never use [(, ([, ((, or >[ shapes.
9. Do NOT use subgraphs.

CORRECT example — follow this format exactly:
```mermaid
graph TD
    A[User Client] --> B[FastAPI Backend]
    B --> C[Analyzer Module]
    B --> D[Generator Module]
    C --> E[Gemini API]
    D --> F[README Output]
```
"""


def build_prompt(
    tree: str,
    stack: Dict[str, List[str]],
    files: List[Dict[str, str]],
    project_name: str,
) -> tuple[str, str]:
    """Build the full Gemini prompt from the analyzed project context.

    Combines the directory tree, detected tech stack, and key file contents
    into a structured prompt that instructs the Gemini model to produce a
    complete ``README.md`` in GitHub-Flavored Markdown.

    Args:
        tree: The directory tree string of the project.
        stack: A dictionary with keys ``languages``, ``frameworks``,
            ``databases``, ``tools``, ``package_managers``.
        files: A list of file dicts with ``path``, ``content``, ``language``.
        project_name: The name of the project.

    Returns:
        A tuple of (system_instruction, user_prompt) to send to Gemini.
    """
    logger.info("Building prompt for project: %s", project_name)

    # Format stack info
    stack_lines: List[str] = []
    for category, items in stack.items():
        if items:
            stack_lines.append(f"- {category.replace('_', ' ').title()}: {', '.join(items)}")
    stack_section = "\n".join(stack_lines) if stack_lines else "No specific stack detected."

    # Format file contents
    file_sections: List[str] = []
    for f in files:
        file_sections.append(
            f"### File: `{f['path']}` ({f['language']})\n```\n{f['content']}\n```"
        )
    files_section = "\n\n".join(file_sections) if file_sections else "No key files analyzed."

    system_instruction = (
        "You are a senior technical writer. Analyze the following project "
        "information and generate a complete, professional README.md file "
        "in GitHub-Flavored Markdown.\n\n"
        "## CRITICAL RULES\n"
        "- Output ONLY the raw Markdown content.\n"
        "- Do NOT wrap the entire output in code fences.\n"
        "- Do NOT add any preamble, explanation, or commentary.\n"
        "- The output must be a valid, complete README.md file ready to save to disk.\n\n"
        "## Instructions\n\n"
        "Generate a complete README.md with the following sections IN THIS EXACT ORDER:\n\n"
        f"1. **# Project Name** — H1 title\n"
        "2. **Badges** — shields.io badges for the primary language and MIT license\n"
        "3. **## Overview** — What the project does, in 2-4 sentences\n"
        "4. **## Features** — Bulleted list of key capabilities\n"
        "5. **## Tech Stack** — Table with columns: Layer | Technology\n"
        "6. **## Project Structure** — The directory tree above inside a code block\n"
        "7. **## Getting Started** — Prerequisites, installation steps, environment setup\n"
        "8. **## Usage** — How to run the project (commands, examples)\n"
        "9. **## API Reference** — If applicable, endpoint table with Method | Path | Description\n"
        "10. **## Architecture** — Include a Mermaid diagram (see rules below)\n"
        "11. **## Contributing** — Brief contribution guidelines\n"
        "12. **## License** — MIT license statement\n\n"
        + MERMAID_INSTRUCTION
    )

    prompt = (
        f"## Project Name\n{project_name}\n\n"
        f"## Directory Structure\n```\n{tree}\n```\n\n"
        f"## Detected Technology Stack\n{stack_section}\n\n"
        f"## Key File Contents\n{files_section}\n"
    )

    return system_instruction, prompt

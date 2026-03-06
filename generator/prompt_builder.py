"""Assembles the complete prompt to send to the Gemini API for README generation."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def build_prompt(
    tree: str,
    stack: Dict[str, List[str]],
    files: List[Dict[str, str]],
    project_name: str,
) -> str:
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
        The assembled prompt string ready to send to Gemini.
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

    prompt = f"""You are a senior technical writer. Analyze the following project information and generate a complete, professional README.md file in GitHub-Flavored Markdown.

## Project Name
{project_name}

## Directory Structure
```
{tree}
```

## Detected Technology Stack
{stack_section}

## Key File Contents
{files_section}

---

## Instructions

Generate a complete README.md with the following sections IN THIS EXACT ORDER:

1. **# {project_name}** — H1 title
2. **Badges** — shields.io badges for the primary language and MIT license
3. **## Overview** — What the project does, in 2–4 sentences
4. **## Features** — Bulleted list of key capabilities
5. **## Tech Stack** — Table with columns: Layer | Technology
6. **## Project Structure** — The directory tree above inside a code block
7. **## Getting Started** — Prerequisites, installation steps, environment setup
8. **## Usage** — How to run the project (commands, examples)
9. **## API Reference** — If applicable, endpoint table with Method | Path | Description
10. **## Architecture** — Include a Mermaid diagram like this:

```mermaid
graph TD
    A[Client] --> B[API Server]
    B --> C[Core Module]
    C --> D[Output]
```

Adjust the diagram nodes to match the actual project architecture based on the detected stack.

11. **## Contributing** — Brief contribution guidelines
12. **## License** — MIT license statement

## CRITICAL RULES
- Output ONLY the raw Markdown content.
- Do NOT wrap the entire output in code fences.
- Do NOT add any preamble, explanation, or commentary.
- The output must be a valid, complete README.md file ready to save to disk.
"""
    return prompt

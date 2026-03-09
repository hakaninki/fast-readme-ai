"""First-time setup script for fast-readme-ai.

This script uses only standard-library modules so it can run before
any project dependencies have been installed.
"""

import os
import shutil
import sys
from pathlib import Path


def main() -> None:
    """Run the fast-readme-ai first-time setup wizard."""
    project_root = Path(__file__).resolve().parent

    print()
    print("⚡ fast-readme-ai — Setup")
    print("=" * 30)
    print()

    # 1. Check Python version
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 11):
        print(f"✘ Python 3.11+ is required, but you have {major}.{minor}")
        sys.exit(1)
    else:
        print(f"✔ Python {major}.{minor} detected")

    # 2. Check / create .env file
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if not env_file.exists():
        if env_example.exists():
            shutil.copy2(env_example, env_file)
            print("✔ .env file created from .env.example")
            print("→ Please open .env and add your GEMINI_API_KEY before continuing.")
        else:
            print("✘ .env.example not found — cannot create .env automatically")
            print("→ Create a .env file manually with your GEMINI_API_KEY")
    else:
        print("✔ .env file found")

    # 3. Check if GEMINI_API_KEY is set
    api_key = ""
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break

    if api_key and api_key != "your_google_gemini_api_key_here":
        print("✔ GEMINI_API_KEY found")
    else:
        print("✘ GEMINI_API_KEY is missing in .env")
        print("→ Get your key at: https://makersuite.google.com/app/apikey")

    # 4. Check dependencies
    print()
    deps = {
        "fastapi": "fastapi",
        "google.genai": "google-genai",
        "typer": "typer",
        "rich": "rich",
    }
    all_ok = True
    for module_name, package_name in deps.items():
        try:
            __import__(module_name)
            print(f"✔ {package_name} installed")
        except ImportError:
            print(f"✘ Missing dependency: {package_name} — run: pip install -e .")
            all_ok = False

    # 5. Final summary
    print()
    if all_ok:
        print("Setup complete. You can now run:")
        print("  fast-readme .")
    else:
        print("Install dependencies first:")
        print("  pip install -e .")
    print()


if __name__ == "__main__":
    main()

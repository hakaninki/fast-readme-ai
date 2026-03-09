"""Google Gemini API integration service for README generation."""

import logging

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


def generate_readme(system_instruction: str, prompt: str) -> str:
    """Send a prompt to the Google Gemini API and return the generated text.

    Initializes the ``google-genai`` client with the configured API
    key, then calls ``generate_content`` with conservative
    temperature settings for consistent output.

    Args:
        system_instruction: Guidelines and behavioral rules for the AI.
        prompt: The payload to generate the README from.

    Returns:
        The raw text response from the Gemini model.

    Raises:
        ValueError: If the ``GEMINI_API_KEY`` environment variable is not set.
        RuntimeError: If the Gemini API call fails for any reason.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    logger.info("Calling Gemini API with model: %s", GEMINI_MODEL)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )

        return response.text

    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

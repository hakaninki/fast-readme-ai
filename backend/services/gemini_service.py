"""Google Gemini API integration service for README generation."""

import logging

import google.generativeai as genai

from backend.config import settings

logger = logging.getLogger(__name__)


def generate_readme(prompt: str) -> str:
    """Send a prompt to the Google Gemini API and return the generated text.

    Initializes the ``google-generativeai`` client with the configured API
    key and model, then calls ``generate_content`` with conservative
    temperature settings for consistent output.

    Args:
        prompt: The fully assembled prompt string to send to Gemini.

    Returns:
        The raw text response from the Gemini model.

    Raises:
        ValueError: If the ``GEMINI_API_KEY`` environment variable is not set.
        RuntimeError: If the Gemini API call fails for any reason.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    model_name = settings.GEMINI_MODEL
    logger.info("Calling Gemini API with model: %s", model_name)

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8192,
            ),
        )

        response = model.generate_content(prompt)
        return response.text

    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

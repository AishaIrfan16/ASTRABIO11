"""Client for RapidAPI's Simple GPT1 moderation endpoint."""
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_URL = "https://simple-gpt1.p.rapidapi.com/moderations"
API_HOST = "simple-gpt1.p.rapidapi.com"
MODEL = "text-moderation-latest"
TIMEOUT_SECONDS = 20


class ModerationError(RuntimeError):
    """Raised when the moderation service cannot return a valid result."""


class ModerationConfigurationError(ModerationError):
    """Raised when required RapidAPI configuration is missing."""


def create_moderation(text: str) -> dict[str, Any]:
    """Send text for moderation and return the provider's JSON result."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text to moderate must be a non-empty string.")

    api_key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not api_key:
        raise ModerationConfigurationError(
            "RAPIDAPI_KEY is missing. Add it to the project-root .env file."
        )

    try:
        response = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": API_HOST,
                "x-rapidapi-key": api_key,
            },
            json={"model": MODEL, "input": text},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise ModerationError("Could not reach the RapidAPI moderation service.") from exc

    if not response.ok:
        raise ModerationError(
            f"RapidAPI moderation request failed with HTTP {response.status_code}."
        )

    try:
        result = response.json()
    except ValueError as exc:
        raise ModerationError("RapidAPI returned invalid JSON.") from exc

    if not isinstance(result, dict):
        raise ModerationError("RapidAPI returned an unexpected response format.")
    return result

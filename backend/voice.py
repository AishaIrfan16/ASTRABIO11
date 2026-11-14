"""FreeTTS text-to-speech client."""
import os
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

TTS_URL = "https://freetts.org/api/v1/tts"
AUDIO_URL = "https://freetts.org/api/audio/"
TIMEOUT_SECONDS = 30


class VoiceError(RuntimeError):
    """Raised when FreeTTS cannot generate or return speech audio."""


class VoiceConfigurationError(VoiceError):
    """Raised when the FreeTTS API key is missing."""


def synthesize(text: str) -> bytes:
    """Generate speech and return the resulting MP3 bytes."""
    api_key = os.getenv("voice_api_key", "").strip() or os.getenv("VOICE_API_KEY", "").strip()
    if not api_key:
        raise VoiceConfigurationError(
            "voice_api_key is missing. Add it to the project-root .env file."
        )

    try:
        response = requests.post(
            TTS_URL,
            headers={"x-api-key": api_key},
            json={
                "text": text,
                "voice": "en-US-AriaNeural",
                "rate": "+0%",
                "pitch": "+0Hz",
                "output_format": "mp3",
            },
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise VoiceError("Could not reach the FreeTTS speech service.") from exc

    if not response.ok:
        raise VoiceError(
            f"FreeTTS speech generation failed with HTTP {response.status_code}."
        )

    try:
        result = response.json()
    except ValueError as exc:
        raise VoiceError("FreeTTS returned invalid JSON.") from exc

    file_id = result.get("file_id") if isinstance(result, dict) else None
    if not isinstance(file_id, str) or not file_id.strip():
        raise VoiceError("FreeTTS returned an unexpected response format.")

    try:
        audio_response = requests.get(
            AUDIO_URL + quote(file_id, safe=""),
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise VoiceError("Could not download the generated FreeTTS audio.") from exc

    if not audio_response.ok:
        raise VoiceError(
            f"FreeTTS audio download failed with HTTP {audio_response.status_code}."
        )
    if not audio_response.content:
        raise VoiceError("FreeTTS returned empty audio.")

    return audio_response.content

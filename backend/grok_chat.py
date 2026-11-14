
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("ASTRA_LLM_TIMEOUT", "20"))


def _api_key():
    return os.getenv("GROQ_API_KEY", "").strip() or os.getenv("API_KEY", "").strip()


def is_configured():
    """Return whether a Groq API key is available."""
    return bool(_api_key())


def ask_groq(prompt, system_prompt=None):
    """Send a chat completion request to Groq and return its text response."""
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("Set GROQ_API_KEY (or the legacy API_KEY) in the environment.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 800,
        "reasoning_effort": "low",
        "include_reasoning": False
    }

    try:
        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Groq chat request failed: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Groq returned invalid JSON.") from exc

    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Groq returned an unexpected response format.") from exc
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Groq returned an empty chat response.")
    return content.strip()


if __name__ == "__main__":
    while True:
        prompt = input("\nYou: ")

        if prompt.lower() in ["exit", "quit"]:
            break

        try:
            answer = ask_groq(prompt)
        except RuntimeError as exc:
            print(f"\nGroq error: {exc}")
        else:
            print("\nGroq:", answer)

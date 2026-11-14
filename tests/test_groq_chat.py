import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import assistant
import grok_chat


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_groq_chat_sends_system_context_and_returns_content(monkeypatch):
    calls = []
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(
        grok_chat.requests,
        "post",
        lambda *args, **kwargs: (
            calls.append((args, kwargs))
            or FakeResponse({"choices": [{"message": {"content": "  Hello, Commander.  "}}]})
        ),
    )

    assert grok_chat.ask_groq("How are you?", "ASTRA context") == "Hello, Commander."
    assert calls[0][1]["headers"]["Authorization"] == "Bearer test-key"
    assert calls[0][1]["json"]["model"] == "openai/gpt-oss-120b"
    assert calls[0][1]["json"]["messages"] == [
        {"role": "system", "content": "ASTRA context"},
        {"role": "user", "content": "How are you?"},
    ]


def test_groq_chat_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        grok_chat.ask_groq("Hello")


def test_groq_chat_accepts_legacy_api_key_name(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("API_KEY", "legacy-test-key")
    monkeypatch.setattr(
        grok_chat.requests,
        "post",
        lambda *args, **kwargs: (
            FakeResponse({"choices": [{"message": {"content": "Ready."}}]})
        ),
    )

    assert grok_chat.ask_groq("Ready?") == "Ready."


def test_groq_is_selected_automatically_when_key_is_configured(monkeypatch):
    monkeypatch.delenv("ASTRA_LLM", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert assistant.provider() == "groq"


def test_default_provider_is_used_when_groq_is_not_configured(monkeypatch):
    monkeypatch.delenv("ASTRA_LLM", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    assert assistant.provider() == "ollama"


def test_groq_failure_retries_with_default_provider(monkeypatch):
    monkeypatch.setenv("ASTRA_LLM", "groq")
    monkeypatch.setattr(assistant, "_ask_groq", lambda *_: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(assistant, "_ask_ollama", lambda *_: "Default model reply.")

    assert assistant.llm_reply("Hello") == "Default model reply."

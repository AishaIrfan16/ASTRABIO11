import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import api
import voice
from main import create_app


class FakeResponse:
    def __init__(self, *, payload=None, content=b"", ok=True, status_code=200):
        self.payload = payload
        self.content = content
        self.ok = ok
        self.status_code = status_code

    def json(self):
        return self.payload


def test_synthesize_uses_project_voice_key_and_downloads_audio(monkeypatch):
    calls = []
    responses = iter([
        FakeResponse(payload={"file_id": "audio-id"}),
        FakeResponse(content=b"mp3 bytes"),
    ])
    monkeypatch.setenv("voice_api_key", "test-key")
    monkeypatch.setattr(
        voice.requests,
        "post",
        lambda *args, **kwargs: (calls.append(("post", args, kwargs)) or next(responses)),
    )
    monkeypatch.setattr(
        voice.requests,
        "get",
        lambda *args, **kwargs: (calls.append(("get", args, kwargs)) or next(responses)),
    )

    assert voice.synthesize("Hello, Commander.") == b"mp3 bytes"
    assert calls[0][2]["headers"] == {"x-api-key": "test-key"}
    assert calls[0][2]["json"]["voice"] == "en-US-AriaNeural"
    assert calls[1][1][0].endswith("/audio/audio-id")


def test_voice_endpoint_returns_audio(monkeypatch):
    monkeypatch.setattr(api.voice, "synthesize", lambda text: b"mp3 bytes")

    response = create_app().test_client().post("/api/voice", json={"text": "Hello"})

    assert response.status_code == 200
    assert response.mimetype == "audio/mpeg"
    assert response.data == b"mp3 bytes"


def test_voice_endpoint_reports_missing_key(monkeypatch):
    monkeypatch.setattr(
        api.voice,
        "synthesize",
        lambda text: (_ for _ in ()).throw(
            voice.VoiceConfigurationError("voice_api_key is missing.")
        ),
    )

    response = create_app().test_client().post("/api/voice", json={"text": "Hello"})

    assert response.status_code == 503
    assert response.get_json()["error"] == "voice_api_key is missing."

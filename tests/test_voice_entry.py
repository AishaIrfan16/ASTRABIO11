import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import api
import assistant
from main import create_app


def test_voice_parse_handles_multiple_metrics_and_blood_pressure():
    parsed = dict(assistant.voice_parse(
        "heart rate 72, blood pressure 120 over 80, blood sugar 95, "
        "temperature 37, sleep 6.5 hours, mood 4"
    ))

    assert parsed == {
        "sys": 120.0,
        "dia": 80.0,
        "hr": 72.0,
        "glucose": 95.0,
        "temp": 37.0,
        "sleep": 6.5,
        "mood": 4.0,
    }


def test_voice_parse_handles_individual_blood_pressure_values():
    parsed = dict(assistant.voice_parse("systolic 122 and diastolic 81"))

    assert parsed == {"sys": 122.0, "dia": 81.0}


def test_checkin_parse_endpoint_returns_values_without_saving(monkeypatch):
    monkeypatch.setattr(api.db, "log_value", lambda *_: pytest.fail("Parsing must not save readings"))
    response = create_app().test_client().post(
        "/api/checkin/parse",
        json={"text": "my pulse is 72 and glucose is 95"},
    )

    assert response.status_code == 200
    assert response.get_json()["values"] == {"hr": 72.0, "glucose": 95.0}


def test_checkin_parse_endpoint_reports_unrecognized_speech():
    response = create_app().test_client().post(
        "/api/checkin/parse",
        json={"text": "hello there"},
    )

    assert response.status_code == 422
    assert response.get_json()["errors"]

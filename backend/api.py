"""HTTP API for ASTRABIO (Flask blueprint). All routes live under /api."""
from flask import Blueprint, Response, jsonify, request

import assistant
import database as db
import moderation
import voice

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/state")
def get_state():
    """Dashboard payload for a mission day: /api/state?day=142"""
    return jsonify(db.state(request.args.get("day", db.DEFAULT_DAY)))


@api_bp.post("/checkin")
def post_checkin():
    """Log measurements: {"values": {"hr": 72, "sleep": 7.5}}. Rejects obvious typos with HTTP 400."""
    vals = (request.get_json(force=True) or {}).get("values", {})
    errs = []
    for k, v in vals.items():
        try:
            ok, msg = db.log_value(k, float(v))
        except (TypeError, ValueError):
            ok, msg = False, f"{k}: not a number"
        if not ok:
            errs.append(msg)
    return jsonify(ok=not errs, errors=errs, checkin=db.checkin_state()), (400 if errs else 200)


@api_bp.post("/checkin/parse")
def parse_checkin_voice():
    """Parse dictated measurements without saving them: {"text": "pulse 72"}."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        return jsonify(ok=False, errors=["Send recognized speech in a 'text' field."]), 400
    values = dict(assistant.voice_parse(payload["text"]))
    if not values:
        return jsonify(ok=False, errors=["No supported measurements found in the speech."]), 422
    return jsonify(ok=True, values=values)


@api_bp.post("/checkin/reset")
def reset_checkin():
    db.reset()
    return jsonify(ok=True)


@api_bp.post("/astra")
def astra():
    """Talk to ASTRA: {"text": "my heart rate is 72", "day": 142}"""
    j = request.get_json(force=True) or {}
    return jsonify(assistant.respond(j.get("text", ""), j.get("day", db.DEFAULT_DAY)))


@api_bp.post("/voice")
def speak():
    """Generate ASTRA speech audio: {"text": "Hello"}."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str) or not payload["text"].strip():
        return jsonify(ok=False, error="Send non-empty text in a 'text' field."), 400
    try:
        audio = voice.synthesize(payload["text"])
    except voice.VoiceConfigurationError as exc:
        return jsonify(ok=False, error=str(exc)), 503
    except voice.VoiceError as exc:
        return jsonify(ok=False, error=str(exc)), 502
    return Response(audio, mimetype="audio/mpeg")


@api_bp.post("/moderate")
def moderate_text():
    """Moderate text using RapidAPI Simple GPT1: {"text": "..."}."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        return jsonify(ok=False, error="Send text in a 'text' field."), 400
    try:
        result = moderation.create_moderation(payload["text"])
    except moderation.ModerationConfigurationError as exc:
        return jsonify(ok=False, error=str(exc)), 503
    except moderation.ModerationError as exc:
        return jsonify(ok=False, error=str(exc)), 502
    return jsonify(ok=True, result=result)

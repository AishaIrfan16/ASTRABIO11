# ASTRABIO

ASTRABIO is a prototype astronaut health and mission-wellbeing dashboard. It combines simulated mission telemetry, a daily measurement check-in, a 3D body map, hazard dashboards, and ASTRA, a voice-first assistant.

> **Prototype and safety notice:** This project uses simulated data and placeholder health ranges. It is not a medical device, clinical decision-support system, or source of medical advice. Do not use it to assess or treat a real person. Real deployment would require validated data, flight-surgeon-approved thresholds, security/privacy controls, and operational review.

## Features

- Mission-day dashboard for radiation, gravity-related health, immunity, mental wellbeing, and habitat conditions.
- Interactive body map with marker status, trends, and hazard filters.
- Daily check-in for heart rate, blood pressure, glucose, temperature, sleep, and mood.
- Rule-based ASTRA assistant with optional Groq, Ollama, or Anthropic rewording.
- Browser speech recognition where supported, browser speech synthesis, and optional FreeTTS MP3 speech.
- Optional RapidAPI text-moderation endpoint.
- CSV-backed simulated mission time series and automated tests for voice parsing and speech service handling.

## Requirements

- Python 3.10 or later (Python 3.11+ recommended).
- A modern browser. Chrome or Edge is recommended for microphone input.
- Optional: a Groq API key, Ollama with a downloaded model, an Anthropic API key, a FreeTTS API key, or a RapidAPI key, depending on which integrations you want to use.

## Quick start

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python backend\main.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). To use another port, set `PORT` before starting the server.

The core dashboard and rule-based responses work without third-party API keys. ASTRA tries Groq when a Groq key is configured; if Groq is not configured or unavailable, it uses the default provider (Anthropic when configured, otherwise Ollama). If that provider is unavailable too, ASTRA uses its built-in rules. Set `ASTRA_LLM=groq` to explicitly prefer Groq, or `ASTRA_LLM=none` for rules only.

## Optional configuration

Create a project-root `.env` file or set environment variables in your shell. Keep real credentials out of source control.

| Variable | Purpose |
| --- | --- |
| `ASTRA_LLM` | `groq`, `ollama`, `anthropic`, or `none`. When omitted, tries Groq if configured, then the default provider (Anthropic if its key is set, otherwise Ollama). |
| `GROQ_API_KEY` | Enables the Groq chat model when configured; also required when `ASTRA_LLM=groq`. The legacy `API_KEY` name is also accepted. |
| `GROQ_MODEL` | Groq model identifier; defaults to `openai/gpt-oss-120b`. |
| `OLLAMA_URL` | Ollama server URL; defaults to `http://localhost:11434`. |
| `OLLAMA_MODEL` | Ollama model name; defaults to `llama3.2:3b`. Pull the model separately when using Ollama. |
| `ANTHROPIC_API_KEY` | Enables Anthropic provider selection when `ASTRA_LLM` is not explicitly set. |
| `ASTRA_MODEL` | Anthropic model name; defaults to `claude-sonnet-4-6`. |
| `ASTRA_LLM_TIMEOUT` | Model request timeout in seconds; defaults to `20`. |
| `VOICE_API_KEY` or `voice_api_key` | FreeTTS key used by `POST /api/voice`. |
| `RAPIDAPI_KEY` | RapidAPI key used by `POST /api/moderate`. |
| `PORT` | Flask listening port; defaults to `5000`. |

Groq, Anthropic, voice generation, and moderation can transmit submitted text (and, for model prompts, simulated status context) to external services. Do not submit sensitive or personal health information to these optional integrations.

## Run tests

```powershell
python -m pytest
```

## API overview

All application endpoints are served under `/api`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/state?day=142` | Return dashboard state for a mission day. |
| `POST` | `/api/checkin` | Validate and log one or more measurements. Body: `{"values":{"hr":72,"sleep":7.5}}`. |
| `POST` | `/api/checkin/parse` | Parse dictated measurements without saving them. Body: `{"text":"pulse 72"}`. |
| `POST` | `/api/checkin/reset` | Reset the in-memory check-in demo state. |
| `POST` | `/api/astra` | Get an assistant reply. Body: `{"text":"my heart rate is 72","day":142}`. |
| `POST` | `/api/voice` | Generate MP3 speech for non-empty text; requires a FreeTTS key. |
| `POST` | `/api/moderate` | Submit text to the configured moderation service; requires a RapidAPI key. |

The detailed project guide documents request/response behavior, data fields, module responsibilities, deployment, and known limitations: [Project documentation (DOCX)](docs/PROJECT_DOCUMENTATION.docx).

## Project layout

```text
backend/       Flask API, dashboard data, ASTRA, voice, and moderation services
frontend/      Single-page dashboard (HTML, CSS, JavaScript)
data/          Simulated mission-day time series (CSV)
models/        Serialized model artifact
notebooks/     Exploratory notebooks
tests/         Pytest tests
docs/          Detailed project documentation
requirements.txt
```

The Flask process serves both the frontend and API. Mission telemetry is read from `data/astronaut_data.csv`; if the file is absent, the backend generates a simulated dataset. Check-in measurements and streak information are held in process memory and reset when the server restarts. The included `models/trained_model.pkl` and notebooks are not loaded by the current web application.

## Production note

The application binds to `0.0.0.0` when started directly. Do not expose it to an untrusted network as-is: production use needs appropriate authentication, transport security, request protections, secrets management, privacy safeguards, persistent data handling, and reviewed medical/operational logic. A Gunicorn entry point is available for compatible deployments:

```text
gunicorn --chdir backend main:app
```

## License

No license file is currently included. All rights and reuse terms should be clarified by the project owner before redistribution or contribution.


<p align="center">



<h3 align="center">Your Health. Your Mission. Our Intelligence.</h3>

<p align="center">
An AI-assisted astronaut health and wellbeing platform designed to detect early health risks, support onboard medical decisions, and protect crew members during long-duration space missions.
</p>

<p align="center">

🌌 1. The Problem

Imagine being hundreds of millions of kilometers away from Earth, where a simple medical emergency could become life-threatening.

During a Mars mission, communication with Earth can experience delays of approximately 22 minutes each way. Communication can also become temporarily unavailable.

Astronauts cannot always wait for instructions from Earth when their health starts deteriorating.

Space missions expose astronauts to multiple interconnected health risks:

Radiation: Exposure to solar particle events and cosmic radiation.
Gravity: Physiological changes caused by prolonged microgravity.
Immunity: Changes in immune function during spaceflight.
Distance: Delayed access to medical support and resources.
Environment: Habitat conditions, sleep disruption, stress, and isolation.

Small health changes can become serious problems if they go unnoticed.

The question is: What if astronauts had an intelligent health companion onboard that could identify problems before they become emergencies?

💡 2. Our Solution — ASTRABIO

ASTRABIO is an AI-assisted astronaut health monitoring and mission-wellbeing platform built to support crew members during long-duration Mars missions.

At its core is ASTRA, an intelligent onboard health companion that monitors astronaut wellbeing, identifies unusual changes, provides understandable guidance, and supports timely medical escalation.

Instead of simply recording health readings, ASTRABIO focuses on identifying changes early and helping astronauts respond appropriately.

What makes ASTRABIO different?
Continuous monitoring of astronaut health and habitat conditions.
Comparison of health readings against reference ranges and individual baselines.
Early identification of potentially concerning changes.
Watch-level explanations and countermeasure suggestions.
Warning-level escalation support for onboard medical personnel.
Voice-enabled interaction and emotional wellbeing support.
An architecture designed with delayed or interrupted Earth communication in mind.

Our mission: Detect early. Act intelligently. Protect the crew.

🖥️ 3. Platform Preview
Landing Page

<p align="center">
<img width="1429" height="952" alt="Screenshot 2026-11-15 200826" src="https://github.com/user-attachments/assets/1cb10052-45b2-4a11-b968-5181a9f4a943" />

The ASTRABIO landing experience introduces the mission and provides access to the platform's core capabilities.

Mission Control Dashboard

<p align="center">
<img width="1899" height="979" alt="Screenshot 2026-11-15 200845" src="https://github.com/user-attachments/assets/a66ecadb-8a57-4c44-a57e-62fd6eaa7bd6" />


The central dashboard brings astronaut health information and mission alerts together in one interface.

It provides an overview of mission status, space-weather alerts, astronaut wellbeing, and access to ASTRA.

Astronaut Body Map & Health Monitoring

<p align="center">
<img width="1833" height="955" alt="Screenshot 2026-11-15 200906" src="https://github.com/user-attachments/assets/7afd3a6f-4549-43e0-a7b9-3ddfe12815be" />


The interactive body map provides a visual representation of health-related risk indicators.

Astronauts can access daily check-ins and monitor important measurements, including:

Resting heart rate
Blood pressure
Blood glucose
Body temperature
Sleep duration
Mood
Radiation Guardian

<p align="center">
<img width="1894" height="975" alt="Screenshot 2026-11-15 200934" src="https://github.com/user-attachments/assets/ac1a92b0-4f50-4ff8-952b-9e40bb06d1dd" />


The Radiation Guardian interface presents radiation-related mission information, dose indicators, space-weather alerts, and astronaut risk visualizations.

🧠 4. Meet ASTRA — Your AI Health Companion

ASTRA is the intelligence layer of ASTRABIO.

It is designed to help astronauts understand health changes without depending entirely on real-time communication with Earth.

ASTRA supports different stages of health monitoring:

Level	ASTRA's Response
🟢 Normal	Continues monitoring and tracking health information.
🟡 Watch	Explains unusual changes and suggests appropriate countermeasures.
🔴 Warning	Supports escalation to onboard medical personnel and guidance based on approved protocols.

At the Warning level, the proposed operational workflow includes medical-officer alerts and repeated flight-surgeon contact until a response is received.

ASTRA also includes a companion experience designed to help astronauts manage stress, isolation, and loneliness during extended missions.

Important: Health classifications are intended to be determined by fixed, validated rules rather than AI-generated decisions. ASTRA is designed to assist, not diagnose.

🛰️ 5. Five Core Health & Mission Modules

ASTRABIO organizes its monitoring capabilities around five major risk areas associated with NASA's RIDGE hazard framework.

☢️ Radiation Guardian

Monitors radiation-related mission information and helps identify potentially concerning exposure conditions.

🪐 Gravity Monitor

Focuses on physiological risks associated with prolonged exposure to altered gravity and microgravity.

🧬 Immune Guardian

Represents immune-health monitoring and potential changes in astronaut immune wellbeing.

🌙 MindSpace

Focuses on mental wellbeing, sleep, mood, stress, and the psychological challenges of isolation.

🏠 Habitat Monitor

Represents environmental and habitat-related conditions that can influence astronaut health and safety.

Together, these modules provide a unified view of astronaut wellbeing throughout the mission.

⚙️ 6. How ASTRABIO Works

The proposed health-monitoring workflow follows a simple cycle:

Collect: Gather astronaut health measurements and habitat information.
Compare: Evaluate readings against reference ranges and individual baselines.
Detect: Identify unusual changes and potential warning signs.
Respond: ASTRA explains the situation and suggests appropriate next steps.
Escalate: Warning-level events are routed toward onboard medical personnel.
Record: Events are timestamped and designed for offline storage and later synchronization.

A change of approximately 15% or more from an individual's baseline is part of the proposed early-detection concept, subject to metric-specific validation.

System Workflow
mermaid
flowchart TD
    A["Astronaut Health & Habitat Data"] --> B["ASTRABIO Monitoring System"]
    B --> C["Baseline & Reference Range Comparison"]
    C --> D{"Risk Classification"}

    D -->|Normal| E["Continue Monitoring"]
    D -->|Watch| F["ASTRA Explanation & Countermeasures"]
    D -->|Warning| G["Medical Escalation Support"]

    F --> H["Record Event"]
    G --> I["Notify Onboard Medical Officer"]
    I --> J["Medical Protocol Guidance"]

    E --> K["Mission Health Records"]
    H --> K
    J --> K

    K --> L["Earth Synchronization When Available"]


This diagram describes the intended system workflow. Not every operational capability is implemented in the current prototype.

🛡️ 7. Safety-First Design

Medical safety is a fundamental principle behind ASTRABIO.

The platform is designed around the following principles:

Rule-based safety: Health warning classifications should be controlled by validated rules, not generated by AI.
Human oversight: ASTRA assists astronauts and medical personnel rather than replacing professional medical judgment.
Protocol-based guidance: Medical recommendations should use approved protocols and account for allergies and medications.
Event traceability: Health-related events should be timestamped and recorded.
Communication resilience: Offline operation and synchronization when communication returns are key design goals.
Privacy: Sensitive astronaut health information must be protected.
ASTRABIO is currently a software prototype using simulated mission data. It is not clinically validated and must not be used for real medical decisions.
🧰 8. Technology Stack
Technology	Purpose
Python	Backend development
Flask	Web application and API
HTML5	Frontend structure
CSS3	Interface styling
JavaScript	Dashboard interactions
CSV	Simulated mission telemetry
Groq	Optional AI integration
Ollama	Optional locally hosted language model
Anthropic	Optional AI integration
Browser Speech APIs	Voice interaction
FreeTTS	Optional speech generation
Pytest	Automated testing
🏗️ 9. Project Architecture
text
ASTRABIO/
│
├── backend/
│   └── main.py
│
├── frontend/
│   ├── HTML files
│   ├── CSS files
│   └── JavaScript files
│
├── data/
│   └── astronaut_data.csv
│
├── models/
│   └── trained_model.pkl
│
├── notebooks/
│
├── tests/
│
├── docs/
│   ├── PROJECT_DOCUMENTATION.docx
│   └── images/
│       ├── astrabio-landing.png
│       ├── astrabio-dashboard.png
│       ├── astrabio-bodymap.png
│       └── astrabio-radiation.png
│
├── requirements.txt
└── README.md


The Flask backend serves the frontend and provides API endpoints for dashboard data, check-ins, ASTRA interactions, and optional integrations.

🚀 10. Getting Started
Prerequisites
Python 3.10 or later (Python 3.11+ recommended).
Git.
A modern web browser.
Optional API credentials for external AI and voice integrations.
Installation

1. Clone the repository

bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ASTRABIO


2. Create a virtual environment

Windows:

powershell
python -m venv .venv
.venv\Scripts\Activate.ps1


Linux / macOS:

bash
python3 -m venv .venv
source .venv/bin/activate


3. Install dependencies

bash
python -m pip install -r requirements.txt


4. Start the Flask application

bash
python backend/main.py


5. Open the application

Visit:

"https://astrabio11-production.up.railway.app/"


Your ASTRABIO mission dashboard should now be available locally.

🔑 11. Optional API Configuration

ASTRABIO supports optional AI, voice, and moderation integrations.

Create a .env file in the project root and configure the services you want to use.

Environment Variable	Description
ASTRA_LLM	Selects the AI provider
GROQ_API_KEY	Groq API authentication
GROQ_MODEL	Groq model selection
OLLAMA_URL	Local Ollama server
OLLAMA_MODEL	Ollama model selection
ANTHROPIC_API_KEY	Anthropic API authentication
ASTRA_MODEL	Anthropic model selection
ASTRA_LLM_TIMEOUT	AI request timeout
VOICE_API_KEY	FreeTTS authentication
RAPIDAPI_KEY	Moderation service authentication
PORT	Flask application port

The built-in rule-based ASTRA responses and core dashboard do not require external AI API keys.

Keep your API credentials private. Never commit your .env file to GitHub.

🧪 12. Running Tests

Run the automated test suite:

bash
python -m pytest


The project includes tests for voice parsing and speech-service handling.

🔌 13. API Endpoints

The Flask application exposes the following API endpoints:

Method	Endpoint	Function
GET	/api/state?day=142	Retrieve mission dashboard state
POST	/api/checkin	Submit astronaut health measurements
POST	/api/checkin/parse	Parse dictated health measurements
POST	/api/checkin/reset	Reset demo check-in state
POST	/api/astra	Interact with ASTRA
POST	/api/voice	Generate speech audio
POST	/api/moderate	Submit text for moderation

Detailed technical information is available in Project Documentation.

🌍 14. Beyond Mars — Real-World Applications

Although ASTRABIO is designed around long-duration Mars missions, its underlying concept can be adapted to other isolated and resource-constrained environments.

Potential applications include:

🧊 Antarctic Research Stations: Monitoring researchers in remote polar environments.
🌊 Submarines: Supporting crew health during extended underwater missions.
🏥 Remote Medical Facilities: Supporting health monitoring where medical resources are limited.
🚀 Space Missions: Supporting astronaut wellbeing during long-duration exploration.

Our vision is to make intelligent health monitoring accessible wherever immediate medical assistance is difficult to obtain.

🔮 15. Future Roadmap

Our future development goals include:

Integration with real wearable health-monitoring devices.
Validated astronaut-specific health baselines.
Improved individual health trend analysis.
Robust offline event storage and Earth synchronization.
Flight-surgeon notification and acknowledgment workflows.
Expanded medical protocol integration.
Enhanced mental-health companion capabilities.
Stronger authentication, encryption, and privacy controls.
Validation with relevant aerospace and medical experts.
🏆 16. Why ASTRABIO?

Traditional monitoring systems primarily focus on collecting and displaying health information.

ASTRABIO aims to take the next step.

It combines health monitoring, early risk identification, AI-assisted communication, mission awareness, and medical escalation support into a unified astronaut health platform.

We are not just monitoring astronaut health. We are helping astronauts stay one step ahead of potential emergencies.

<p align="center">
<h2>🌌 ASTRABIO</h2>
<h3>Because Every Life Matters, Even Millions of Kilometers Away.</h3>
<i>Built for the future of human space exploration.</i>
</p>

<p align="center">
⭐ If you find this project interesting, consider giving the repository a star!
</p>

<p align="center">
<b>Explore Beyond Earth. Protect Life Everywhere. 🚀</b>
</p>

⚠️ Disclaimer

ASTRABIO is an experimental hackathon/research prototype. It currently uses simulated data and is not a certified medical device. Its health indicators, thresholds, AI responses, and proposed medical workflows have not been clinically validated. The platform is intended for demonstration and development purposes only.

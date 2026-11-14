"""ASTRABIO entry point: serves the frontend and the /api routes.

    cd backend && python main.py          # http://127.0.0.1:5000  (Chrome or Edge for voice)
    gunicorn --chdir backend main:app     # production
"""
import os
from pathlib import Path

from flask import Flask, send_from_directory

from api import api_bp

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


def create_app():
    app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND, "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

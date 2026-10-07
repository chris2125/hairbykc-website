import logging
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = BASE_DIR / "instance" / "appointments.sqlite3"
PUBLIC_ASSET_SUFFIXES = {".css", ".js", ".jpg", ".jpeg", ".png"}


def create_app(database_path: Optional[Path] = None) -> Flask:
    app = Flask(__name__, static_folder=None)
    db_path = Path(database_path or os.environ.get("HAIRBYKC_DATABASE", DEFAULT_DATABASE))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                style TEXT NOT NULL,
                preferred_date TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )

    @app.get("/")
    def homepage():
        return send_from_directory(BASE_DIR, "index.html")

    @app.get("/<path:filename>")
    def public_asset(filename: str):
        asset_path = Path(filename)
        if asset_path.suffix.lower() not in PUBLIC_ASSET_SUFFIXES:
            return jsonify(error="Not found."), 404
        return send_from_directory(BASE_DIR, filename)

    @app.post("/api/bookings")
    def create_booking():
        try:
            data = request.get_json()
        except BadRequest:
            return jsonify(error="Request body must contain valid JSON."), 400

        if not isinstance(data, dict):
            return jsonify(error="Request body must be a JSON object."), 400

        values = {}
        limits = {"name": 100, "phone": 40, "style": 100, "details": 1000}
        for field, limit in limits.items():
            value = data.get(field, "")
            if not isinstance(value, str):
                return jsonify(error=f"{field.replace('_', ' ').capitalize()} must be text."), 400
            value = value.strip()
            if field != "details" and not value:
                return jsonify(error=f"{field.replace('_', ' ').capitalize()} is required."), 400
            if len(value) > limit:
                return jsonify(error=f"{field.replace('_', ' ').capitalize()} must be {limit} characters or fewer."), 400
            values[field] = value

        preferred_date = data.get("preferred_date")
        if not isinstance(preferred_date, str):
            return jsonify(error="Preferred date is required in YYYY-MM-DD format."), 400
        try:
            requested_date = date.fromisoformat(preferred_date)
        except ValueError:
            return jsonify(error="Preferred date must be a valid YYYY-MM-DD date."), 400
        if requested_date < date.today():
            return jsonify(error="Preferred date cannot be in the past."), 400

        try:
            with closing(sqlite3.connect(db_path, timeout=5)) as connection, connection:
                connection.execute(
                    """
                    INSERT INTO bookings (name, phone, style, preferred_date, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        values["name"],
                        values["phone"],
                        values["style"],
                        requested_date.isoformat(),
                        values["details"],
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
        except sqlite3.Error:
            app.logger.exception("Could not save appointment request")
            return jsonify(error="We couldn't save your request. Please try again later."), 500

        return jsonify(message="Your appointment request was saved. We'll be in touch soon."), 201

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=5000)

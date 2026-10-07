import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

from app import create_app


class BookingApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "bookings.sqlite3"
        self.app = create_app(self.database_path)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def valid_booking(self):
        return {
            "name": "Casey Example",
            "phone": "+353 83 000 0000",
            "style": "Box braids",
            "preferred_date": (date.today() + timedelta(days=7)).isoformat(),
            "details": "Shoulder length",
        }

    def test_booking_is_saved_and_returns_confirmation(self):
        response = self.client.post(
            "/api/bookings",
            data=json.dumps(self.valid_booking()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("saved", response.get_json()["message"])
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            saved = connection.execute(
                "SELECT name, phone, style, preferred_date, details FROM bookings"
            ).fetchone()
        self.assertEqual(
            saved,
            (
                "Casey Example",
                "+353 83 000 0000",
                "Box braids",
                self.valid_booking()["preferred_date"],
                "Shoulder length",
            ),
        )

    def test_invalid_booking_is_rejected_without_saving(self):
        booking = self.valid_booking()
        booking["preferred_date"] = (date.today() - timedelta(days=1)).isoformat()
        response = self.client.post(
            "/api/bookings",
            data=json.dumps(booking),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("past", response.get_json()["error"])
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            count = connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        self.assertEqual(count, 0)

    def test_nested_jpeg_asset_is_served(self):
        response = self.client.get("/Braids/French%20Braids.jpeg")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/jpeg")
        response.close()

    def test_favicon_is_served(self):
        response = self.client.get("/favicon.png")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")
        response.close()


if __name__ == "__main__":
    unittest.main()

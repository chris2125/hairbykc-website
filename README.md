# HairbyKC

This is a Flask-backed website. Appointment requests submitted from the booking
form are stored in a local SQLite database.

## Run locally

Install Python 3.9 or newer, then from this folder run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in a browser. The app creates
`instance/appointments.sqlite3` the first time it starts. Set the
`HAIRBYKC_DATABASE` environment variable to use a different database file.

The booking API is `POST /api/bookings`. It accepts JSON with `name`, `phone`,
`style`, `preferred_date` (`YYYY-MM-DD`), and optional `details` fields.
Requests are validated server-side; there is no public endpoint for reading
customer bookings.

For a live site, deploy the Flask app and database to a Python-capable host and
configure persistent storage for the SQLite file. Do not use the local
development server as a production server.

## Deploy to Render

The `render.yaml` Blueprint configures a free Render web service in Frankfurt.
To deploy it, push this repository to GitHub, sign in to Render, choose **New
> Blueprint**, connect this repository, and apply the Blueprint. Render will
provide a URL ending in `onrender.com`; the `hairbykc` name is subject to
availability and can be changed in the Blueprint before creation.

The free web service may sleep when idle, and its local filesystem is temporary.
Because appointment requests currently use SQLite, booking data can be lost
when the service restarts, sleeps, or redeploys. Use persistent database
storage before relying on this deployment for real appointment requests.

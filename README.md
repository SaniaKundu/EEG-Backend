# Backend (Flask) — local dev

This Flask backend implements `/detect-mood` to accept an image (`image`) and an EEG CSV (`eeg`) and returns a mood + music link.

Setup
```
python -m venv .venv
.venv\Scripts\activate  # on Windows (PowerShell/CMD)
pip install -r requirements.txt
```

Create a `.env` file in `backend/` by copying `.env.example` and filling values (do not commit `.env`).

Run (dev):
```
python app.py
```

Endpoints
- `GET /` – simple health check
- `POST /detect-mood` – accepts multipart form data. Fields:
  - `image` (file)
  - `eeg` (file, optional)
Quick test

- A small test script is provided at `scripts/run-test.sh` which will post sample files in `samples/` to the running backend. Example:

```
./scripts/run-test.sh http://127.0.0.1:5000
```
Note: `deepface` can require large ML dependencies; install carefully if you only need a placeholder. Modify `database.py` to connect to your MongoDB.

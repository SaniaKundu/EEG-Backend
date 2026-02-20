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

---

## DeepFace troubleshooting (Render / production)

- Use the **Docker** environment in Render for reliable system dependencies (OpenCV, ffmpeg, etc.).
- Ensure instance memory is >= 1–2GB; DeepFace/TensorFlow can fail on very small plans.
- After deploy, call the diagnostics endpoint to see module availability and versions:

  `GET https://<your-service>/diagnostics`

  It returns `deepface.available`, `deepface.error`, TensorFlow/OpenCV versions, and useful env values.

- If `deepface` is not available or `tensorflow` import fails, check the **build logs** for pip install / wheel errors and increase instance memory or switch to Docker.
- For persistent failure, you can disable DeepFace locally and still use EEG-only mode — the UI will show `Neutral` when face analysis is unavailable.


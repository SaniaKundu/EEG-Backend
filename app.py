from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

from face_emotion import detect_face_emotion
from eeg_reader import read_eeg_emotion
from mood_logic import combine_mood
from music_recommendation import get_music_link, get_music_list
from database import save_result

app = Flask(__name__)

# Configure CORS origins via environment variable `CORS_ORIGINS` (comma-separated).
# If not set, allow localhost Vite dev origins by default for development.
from dotenv import load_dotenv
load_dotenv()

cors_env = os.getenv("CORS_ORIGINS")
if cors_env:
    origins = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    # Default development origins — includes Vite/CRA ports (3000 and 5173+)
    origins = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176",
        "http://localhost:5177", "http://127.0.0.1:5177",
        "https://emotion-detection-7y82.vercel.app",
    ]

CORS(app, origins=origins, supports_credentials=True)
print("CORS allowed origins:", origins)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Mood Detection Backend Running"

@app.route("/detect-mood", methods=["POST"])
def detect_mood():

    face_file = request.files.get("image")
    eeg_file = request.files.get("eeg")

    if not face_file:
        return jsonify({"error": "Face image missing"}), 400

    face_path = os.path.join(UPLOAD_FOLDER, face_file.filename)
    face_file.save(face_path)

    face_emotion = detect_face_emotion(face_path)

    if eeg_file:
        eeg_path = os.path.join(UPLOAD_FOLDER, eeg_file.filename)
        eeg_file.save(eeg_path)
        eeg_emotion = read_eeg_emotion(file_path=eeg_path)
    else:
        eeg_emotion = read_eeg_emotion(device=True)

    final_mood = combine_mood(face_emotion, eeg_emotion)
    # Fetch a list of music options for the final mood
    music_options = get_music_list(final_mood, limit=5)
    # Pick first as primary link
    music_link = music_options[0]['url'] if music_options else get_music_link(final_mood)

    save_result(face_emotion, eeg_emotion, final_mood, music_link)

    return jsonify({
        "face_emotion": face_emotion,
        "eeg_emotion": eeg_emotion,
        "final_mood": final_mood,
        "music_link": music_link,
        "music_options": music_options,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/mood-music', methods=['GET'])
def get_mood_music():
    mood = request.args.get('mood', '')
    items = get_music_list(mood, limit=20)
    return jsonify({'mood': mood, 'tracks': items})


@app.route('/mood-music', methods=['POST'])
def add_mood_music():
    # Protected by SECRET_KEY in header X-SECRET
    secret = os.getenv('SECRET_KEY')
    header = request.headers.get('X-SECRET')
    if not secret or header != secret:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        payload = request.get_json()
        mood = payload.get('mood')
        tracks = payload.get('tracks')
        if not mood or not tracks:
            return jsonify({'error': 'mood and tracks required'}), 400

        # Save to Mongo if available
        from database import db
        if db:
            coll = db['mood_music']
            coll.update_one({'mood': mood.lower()}, {'$set': {'tracks': tracks}}, upsert=True)
            return jsonify({'ok': True})
        else:
            return jsonify({'error': 'DB not configured'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # Bind to the PORT environment variable (required by Railway/Heroku/etc.)
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)

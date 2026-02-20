from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    # For local dev, allow proceeding without DB (prints only)
    print("Warning: MONGO_URI not set. Database operations will be skipped.")
    client = None
    db = None
else:
    client = MongoClient(MONGO_URI)
    db = client["mood_detection_db"]

results = db["results"] if db else None
mood_records = db["mood_records"] if db else None

def save_result(face_emotion, eeg_emotion, final_mood, music_link):
    data = {
        "face_emotion": face_emotion,
        "eeg_emotion": eeg_emotion,
        "final_mood": final_mood,
        "music_link": music_link,
        "timestamp": datetime.now()
    }

    if results and mood_records:
        results.insert_one(data)
        mood_records.insert_one(data)
        print("Saved in MongoDB")
    else:
        print("DB not configured; skipping save. Data:", data)

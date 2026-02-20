try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception:
    DEEPFACE_AVAILABLE = False

def detect_face_emotion(image_path):
    if not DEEPFACE_AVAILABLE:
        print("DeepFace not installed — returning Neutral by default.")
        return "Neutral"

    try:
        result = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion"],
            enforce_detection=False
        )

        if isinstance(result, list):
            result = result[0]

        raw = result.get("dominant_emotion", "Neutral")
        # DeepFace returns lowercase (e.g., 'happy', 'sad', 'angry', 'fear',
        # 'surprise', 'disgust', 'neutral'). Normalize to Title case.
        return str(raw).strip().title()

    except Exception as e:
        print("Face emotion error:", e)
        return "Neutral"

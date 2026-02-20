import os
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    DEEPFACE_ERROR = None
except Exception as _err:
    DEEPFACE_AVAILABLE = False
    DEEPFACE_ERROR = str(_err)


def get_deepface_info():
    """Return diagnostic info about DeepFace/TensorFlow/OpenCV availability."""
    info = {"available": DEEPFACE_AVAILABLE, "error": DEEPFACE_ERROR}
    if DEEPFACE_AVAILABLE:
        try:
            import deepface as _df
            info["deepface_version"] = getattr(_df, "__version__", None)
        except Exception as e:
            info["deepface_version"] = str(e)
        try:
            import tensorflow as tf
            info["tensorflow_version"] = getattr(tf, "__version__", None)
        except Exception as e:
            info["tensorflow_version"] = str(e)
        try:
            import cv2
            info["opencv_version"] = getattr(cv2, "__version__", None)
        except Exception as e:
            info["opencv_version"] = str(e)
    return info


def detect_face_emotion(image_path):
    # If DeepFace isn't available, return Neutral and log the reason.
    if not DEEPFACE_AVAILABLE:
        print("DeepFace not installed — returning Neutral by default. error:", DEEPFACE_ERROR)
        return "Neutral"

    try:
        result = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion"],
            enforce_detection=False
        )

        # Some DeepFace versions return a list; normalize to dict
        if isinstance(result, list):
            result = result[0]

        # Log raw result when in debug mode to help diagnose misclassifications.
        if os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes"):
            print("DeepFace raw analyze result:", result)

        raw = result.get("dominant_emotion", "Neutral")
        return str(raw).strip().title()

    except Exception as e:
        # Log exception details so you can inspect Render logs.
        print("Face emotion error:", type(e).__name__, e)
        return "Neutral"

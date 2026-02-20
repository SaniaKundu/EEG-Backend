def combine_mood(face_emotion, eeg_emotion):
    """Normalize inputs and combine face + EEG emotions into a single mood.

    This function normalizes casing (e.g., 'happy' -> 'Happy') so detectors
    returning lowercase strings don't get lost. Priority ordering is:
    exact match -> Sad -> Angry -> Happy -> Calm -> Neutral
    """

    # Normalize to Title case strings for consistent comparisons
    def _norm(x):
        try:
            return str(x).strip().title()
        except Exception:
            return "Neutral"

    f = _norm(face_emotion)
    e = _norm(eeg_emotion)

    if f == e:
        return f

    if "Sad" in (f, e):
        return "Sad"

    if "Angry" in (f, e):
        return "Angry"

    if "Fear" in (f, e):
        return "Fear"

    if "Happy" in (f, e):
        return "Happy"

    if "Calm" in (f, e):
        return "Calm"

    return "Neutral"

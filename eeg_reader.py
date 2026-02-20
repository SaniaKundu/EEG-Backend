import pandas as pd

def read_eeg_emotion(file_path=None, device=False):

    try:
        # =========================
        # Case 1: CSV file uploaded
        # =========================
        if file_path:
            df = pd.read_csv(file_path)

            # Take last row (latest signal)
            row = df.iloc[-1]

            print("Detected EEG Columns:", df.columns.tolist())

            # Initialize
            alpha = beta = theta = gamma = delta = 0
            attention = meditation = 50

            # ===== NeuroSky MindWave =====
            if "attention" in df.columns:
                attention = float(row["attention"])
                meditation = float(row["meditation"])

                delta = float(row["delta"])
                theta = float(row["theta"])
                alpha = float(row["lowAlpha"]) + float(row["highAlpha"])
                beta = float(row["lowBeta"]) + float(row["highBeta"])
                gamma = float(row["lowGamma"]) + float(row["highGamma"])

            # ===== Muse Headband =====
            elif {"alpha","beta","theta","gamma"}.issubset(df.columns):
                alpha = float(row["alpha"])
                beta = float(row["beta"])
                theta = float(row["theta"])
                gamma = float(row["gamma"])
                delta = theta  # approx

                attention = 50
                meditation = 50

            # ===== Emotiv EPOC =====
            elif "AF3" in df.columns:
                channels = row[1:].astype(float)
                avg = channels.mean()

                alpha = avg * 0.30
                beta = avg * 0.25
                theta = avg * 0.20
                gamma = avg * 0.15
                delta = avg * 0.10

                attention = 50
                meditation = 50

            else:
                return "Unknown"

            # =========================
            # Safe calculation
            # =========================
            total = alpha + beta + theta + gamma + delta
            if total == 0:
                return "Neutral"

            alpha_ratio = alpha / total
            beta_ratio = beta / total
            theta_ratio = theta / total
            gamma_ratio = gamma / total

            print("Ratios:", alpha_ratio, beta_ratio, theta_ratio, gamma_ratio)
            print("Attention:", attention, "Meditation:", meditation)

            # =========================
            # Improved Emotion Logic
            # =========================
            if attention < 40 and meditation < 40 and theta_ratio > alpha_ratio:
                return "Sad"

            elif beta_ratio > alpha_ratio and meditation < 40:
                return "Angry"

            elif attention > 60 and meditation > 60 and alpha_ratio > beta_ratio:
                return "Happy"

            elif attention >= 40 and meditation >= 40 and alpha_ratio >= theta_ratio:
                return "Calm"

            else:
                return "Neutral"


        # =========================
        # Case 2: Device fallback
        # =========================
        if device:
            # Here you can later integrate real device logic (serial/brainflow)
            print("EEG device connected (simulated)")
            return "Neutral"

    except Exception as e:
        print("EEG error:", e)
        return "Neutral"

from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

MODEL_FILE = (
    BASE_DIR
    / "model"
    / "anomaly_model.pkl"
)


class AnomalyAI:

    def __init__(self):

        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Anomaly AI model not found:\n"
                f"{MODEL_FILE}\n\n"
                "Please run:\n"
                "python anomaly_ai/train_model.py"
            )

        self.model = joblib.load(
            MODEL_FILE
        )

        self.features = [
            "train_speed",
            "train_distance",
            "track_occupancy",
            "signal_state",
            "current_delay",
            "next_train_distance",
            "station_distance"
        ]

    def predict(
        self,
        train_speed,
        train_distance,
        track_occupancy,
        signal_state,
        current_delay,
        next_train_distance,
        station_distance
    ):

        data = pd.DataFrame([{
            "train_speed": train_speed,
            "train_distance": train_distance,
            "track_occupancy": track_occupancy,
            "signal_state": signal_state,
            "current_delay": current_delay,
            "next_train_distance": next_train_distance,
            "station_distance": station_distance
        }])

        # AI prediction
        prediction = self.model.predict(data)[0]

        # Anomaly score
        score = self.model.decision_function(data)[0]

        is_anomaly = prediction == -1

        # Convert score into a simple risk percentage
        risk_percentage = max(
            0,
            min(
                100,
                (0.10 - score) * 500
            )
        )

        # Risk level
        if risk_percentage >= 70:
            risk_level = "HIGH"

        elif risk_percentage >= 40:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"

        return {
            "anomaly_detected": bool(
                is_anomaly
            ),
            "anomaly_score": round(
                float(score),
                4
            ),
            "risk_percentage": round(
                float(risk_percentage),
                2
            ),
            "risk_level": risk_level
        }
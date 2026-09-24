from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

MODEL_FILE = BASE_DIR / "model" / "conflict_model.pkl"


class ConflictAI:

    def __init__(self):

        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Conflict AI model not found:\n{MODEL_FILE}\n\n"
                "Please run:\n"
                "python conflict_ai/train_model.py"
            )

        self.model = joblib.load(MODEL_FILE)

        self.features = [
            "train_a_distance",
            "train_a_speed",
            "train_b_distance",
            "train_b_speed",
            "same_junction",
            "conflicting_route",
            "track_occupied",
            "signal_a",
            "signal_b",
            "time_a",
            "time_b",
            "arrival_difference"
        ]

    def predict(
        self,
        train_a_distance,
        train_a_speed,
        train_b_distance,
        train_b_speed,
        same_junction,
        conflicting_route,
        track_occupied,
        signal_a,
        signal_b
    ):

        # Calculate estimated time to junction
        time_a = train_a_distance / max(train_a_speed, 1)

        time_b = train_b_distance / max(train_b_speed, 1)

        # Difference between arrival times
        arrival_difference = abs(
            time_a - time_b
        )

        data = pd.DataFrame([{
            "train_a_distance": train_a_distance,
            "train_a_speed": train_a_speed,
            "train_b_distance": train_b_distance,
            "train_b_speed": train_b_speed,
            "same_junction": same_junction,
            "conflicting_route": conflicting_route,
            "track_occupied": track_occupied,
            "signal_a": signal_a,
            "signal_b": signal_b,
            "time_a": time_a,
            "time_b": time_b,
            "arrival_difference": arrival_difference
        }])

        # Prediction
        prediction = self.model.predict(data)[0]

        # Probability
        probabilities = self.model.predict_proba(data)[0]

        conflict_probability = probabilities[1]

        # Risk level
        if conflict_probability >= 0.75:
            risk_level = "HIGH"

        elif conflict_probability >= 0.40:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"

        return {
            "conflict_detected": bool(prediction),
            "conflict_probability": round(
                float(conflict_probability),
                4
            ),
            "risk_percentage": round(
                float(conflict_probability) * 100,
                2
            ),
            "risk_level": risk_level,
            "time_a": round(time_a, 2),
            "time_b": round(time_b, 2),
            "arrival_difference": round(
                arrival_difference,
                2
            )
        }
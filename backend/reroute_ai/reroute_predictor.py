from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

MODEL_FILE = (
    BASE_DIR
    / "model"
    / "reroute_model.pkl"
)


class RerouteAI:

    def __init__(self):

        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Reroute AI model not found:\n"
                f"{MODEL_FILE}\n\n"
                "Please run:\n"
                "python reroute_ai/train_model.py"
            )

        self.model = joblib.load(MODEL_FILE)

    def predict(
        self,
        original_route_distance,
        alternative_route_distance,
        incident_type,
        route_blocked,
        alternative_available,
        alternative_signal_available,
        alternative_conflict_risk,
        alternative_restriction,
        current_delay
    ):

        additional_distance = (
            alternative_route_distance
            - original_route_distance
        )

        data = pd.DataFrame([{
            "original_route_distance":
                original_route_distance,

            "alternative_route_distance":
                alternative_route_distance,

            "incident_type":
                incident_type,

            "route_blocked":
                route_blocked,

            "alternative_available":
                alternative_available,

            "alternative_signal_available":
                alternative_signal_available,

            "alternative_conflict_risk":
                alternative_conflict_risk,

            "alternative_restriction":
                alternative_restriction,

            "current_delay":
                current_delay,

            "additional_distance":
                additional_distance
        }])

        # AI probability
        probabilities = self.model.predict_proba(data)[0]

        reroute_probability = float(
            probabilities[1]
        )

        # --------------------------------------------------
        # Safety/business rules
        # --------------------------------------------------

        # No actual incident = NEVER reroute.
        if incident_type == 0:
            reroute = False
            reason = "No actual incident affecting the route."

        # Original route must actually be blocked.
        elif route_blocked != 1:
            reroute = False
            reason = "Original route is not blocked."

        # Alternative route must exist.
        elif alternative_available != 1:
            reroute = False
            reason = "No alternative route is available."

        # Alternative route must have signal availability.
        elif alternative_signal_available != 1:
            reroute = False
            reason = "Alternative route has no signal availability."

        # Alternative route must not have a serious conflict.
        elif alternative_conflict_risk >= 0.60:
            reroute = False
            reason = "Alternative route has high conflict risk."

        # Existing restriction prevents rerouting.
        elif alternative_restriction == 1:
            reroute = False
            reason = "Alternative route has an active restriction."

        # AI decision.
        else:
            reroute = reroute_probability >= 0.40

            if reroute:
                reason = "AI recommends the available alternative route."
            else:
                reason = "AI does not recommend rerouting."

        # --------------------------------------------------
        # Incident names
        # --------------------------------------------------

        incident_names = {
            0: "NONE",
            1: "TRACK FAILURE",
            2: "TRACK BLOCKAGE",
            3: "SIGNAL FAILURE",
            4: "MAINTENANCE BLOCK",
            5: "EMERGENCY / OBSTRUCTION"
        }

        return {
            "reroute_recommended": bool(reroute),

            "reroute_probability": round(
                reroute_probability,
                4
            ),

            "reroute_percentage": round(
                reroute_probability * 100,
                2
            ),

            "incident": incident_names.get(
                incident_type,
                "UNKNOWN"
            ),

            "additional_distance": round(
                additional_distance,
                2
            ),

            "reason": reason
        }
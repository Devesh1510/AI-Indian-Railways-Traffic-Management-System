import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class IncidentResponseAI:

    def __init__(self):
        self.name = "Railway Incident Response AI"

    def analyze(self, railway_data):

        # --------------------------------------------------
        # AUTOMATIC INCIDENT DETECTION FROM LIVE STATE
        # --------------------------------------------------

        # A manually controlled RED signal is treated as an
        # operational restriction, not automatically as a
        # signal failure.
        if str(railway_data.get("incident", "NONE")).upper() == "NONE":

            signals = railway_data.get("signals_state", [])

            for signal in signals:

                signal_status = str(
                    signal.get("status", "")
                ).upper()

                signal_mode = str(
                    signal.get("mode", "")
                ).upper()

                if signal_status == "RED" and signal_mode == "MANUAL":

                    railway_data["incident"] = (
                        "MANUAL SIGNAL RESTRICTION"
                    )

                    railway_data["section"] = (
                        signal.get("signal_id", "UNKNOWN")
                    )

                    controlled_train = next(
                        (
                            train
                            for train in railway_data.get("trains", [])
                            if train.get("controlling_signal")
                            == signal.get("signal_id")
                        ),
                        None
                    )

                    if controlled_train:
                        railway_data["train_id"] = (
                            controlled_train.get(
                                "train_id",
                                "UNKNOWN"
                            )
                        )

                    break

        incident = str(
            railway_data.get("incident", "NONE")
        ).upper()

        train_id = railway_data.get(
            "train_id",
            "UNKNOWN"
        )

        section = railway_data.get(
            "section",
            "UNKNOWN"
        )

        congestion = str(
            railway_data.get(
                "congestion_level",
                "UNKNOWN"
            )
        ).upper()

        conflict = railway_data.get(
            "conflict"
        )

        anomaly = railway_data.get(
            "anomaly"
        )

        reroute = railway_data.get(
            "reroute_recommended"
        )

        reroute_reason = railway_data.get(
            "reason"
        )

        recommended_signal = railway_data.get(
            "recommended_signal"
        )

        delay = railway_data.get(
            "delay_prediction"
        )

        recommendations = []
        conditions = []

        # --------------------------------------------------
        # INCIDENT
        # --------------------------------------------------

        if incident == "NONE":

            incident_status = (
                "No active operational incident "
                "was reported."
            )

        else:

            incident_status = (
                f"Active incident reported: {incident}."
            )

            recommendations.append(
                "Monitor the affected railway section "
                "and verify the incident status."
            )

        # --------------------------------------------------
        # ANOMALY
        # --------------------------------------------------

        if anomaly is True:

            conditions.append(
                "Anomaly AI detected an unusual "
                "traffic condition."
            )

            recommendations.append(
                "Investigate the abnormal traffic "
                "condition before taking further action."
            )

        elif anomaly is False:

            conditions.append(
                "Anomaly AI did not detect an unusual "
                "traffic condition."
            )

        # --------------------------------------------------
        # CONGESTION
        # --------------------------------------------------

        if congestion == "HIGH":

            conditions.append(
                "Network Congestion AI reports HIGH "
                "congestion."
            )

            recommendations.append(
                "Monitor train spacing and congestion "
                "on the affected section."
            )

        elif congestion == "MEDIUM":

            conditions.append(
                "Network Congestion AI reports MEDIUM "
                "congestion."
            )

            recommendations.append(
                "Continue monitoring the affected section."
            )

        elif congestion == "LOW":

            conditions.append(
                "Network Congestion AI reports LOW "
                "congestion."
            )

        # --------------------------------------------------
        # CONFLICT
        # --------------------------------------------------

        if conflict is True:

            conditions.append(
                "Conflict AI detected a potential "
                "train conflict."
            )

            recommendations.append(
                "Verify train separation and conflicting "
                "routes before authorizing movement."
            )

        elif conflict is False:

            conditions.append(
                "Conflict AI does not currently detect "
                "a predicted conflict."
            )

        # --------------------------------------------------
        # REROUTING
        # --------------------------------------------------

        if reroute is True:

            conditions.append(
                "Reroute AI recommends an alternative route."
            )

            recommendations.append(
                "Evaluate the AI-recommended alternative "
                "route against the current operational "
                "conditions."
            )

        elif reroute is False:

            if reroute_reason:

                conditions.append(
                    f"Reroute AI: {reroute_reason}"
                )

            else:

                conditions.append(
                    "Reroute AI does not recommend "
                    "rerouting."
                )

        # --------------------------------------------------
        # DELAY
        # --------------------------------------------------

        if delay is not None:

            if delay >= 15:

                conditions.append(
                    f"Predicted delay is approximately "
                    f"{delay} minutes."
                )

                recommendations.append(
                    "Consider timetable impact and "
                    "downstream train interactions."
                )

            elif delay >= 5:

                conditions.append(
                    f"Predicted delay is approximately "
                    f"{delay} minutes."
                )

            else:

                conditions.append(
                    f"Predicted delay is approximately "
                    f"{delay} minutes."
                )

        # --------------------------------------------------
        # SIGNAL
        # --------------------------------------------------

        if recommended_signal:

            conditions.append(
                f"Signal AI recommends "
                f"{recommended_signal}."
            )

            recommendations.append(
                "Apply the signal recommendation only "
                "after deterministic safety checks and "
                "operator verification."
            )

        # --------------------------------------------------
        # GENERAL INCIDENT RESPONSE
        # --------------------------------------------------

        if incident != "NONE":

            recommendations.append(
                "Keep Manual Override available for "
                "authorized operator intervention."
            )

        # Remove duplicate recommendations
        recommendations = list(
            dict.fromkeys(recommendations)
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        response = {
            "incident_status": incident_status,
            "affected_train": train_id,
            "affected_section": section,
            "conditions": conditions,
            "recommendations": recommendations,
            "operator_control": (
                "AI provides decision support only. "
                "Final operational control remains "
                "with the authorized operator."
            )
        }

        return response


if __name__ == "__main__":

    ai = IncidentResponseAI()

    result = ai.analyze({
        "train_id": "TRAIN_101",
        "section": "J1_J2",
        "incident": "TRACK BLOCKAGE",
        "congestion_level": "HIGH",
        "conflict": False,
        "anomaly": True,
        "reroute_recommended": True,
        "reason": "AI recommends the available alternative route.",
        "recommended_signal": "RED",
        "delay_prediction": 18
    })

    print()
    print("=" * 70)
    print("RAILWAY INCIDENT RESPONSE AI")
    print("=" * 70)
    print()

    print(result)
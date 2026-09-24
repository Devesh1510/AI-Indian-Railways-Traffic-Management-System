import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class RailwayAssistant:

    def __init__(self):
        self.name = "Railway AI Assistant"
        self.description = (
            "AI assistant for the Indian Railways "
            "Traffic Management System"
        )

    # ---------------------------------------------------------
    # QUESTION CLASSIFICATION
    # ---------------------------------------------------------

    def classify_question(self, question):
        question = question.lower().strip()

        if any(word in question for word in [
            "why",
            "cause",
            "reason",
            "root cause"
        ]):
            return "root_cause"

        if any(word in question for word in [
            "delay", "late", "delayed"
        ]):
            return "delay"

        if any(word in question for word in [
            "congestion",
            "congested",
            "crowded",
            "traffic",
            "busy"
        ]):
            return "congestion"

        if any(word in question for word in [
            "conflict",
            "collision",
            "crossing"
        ]):
            return "conflict"

        if any(word in question for word in [
            "anomaly",
            "abnormal",
            "unusual",
            "problem"
        ]):
            return "anomaly"

        if any(word in question for word in [
            "reroute",
            "rerouting",
            "alternative route",
            "route"
        ]):
            return "reroute"

        if any(word in question for word in [
            "timetable",
            "schedule",
            "platform",
            "departure",
            "arrival"
        ]):
            return "timetable"

        if any(word in question for word in [
            "signal",
            "red",
            "yellow",
            "green"
        ]):
            return "signal"

        return "general"

    # ---------------------------------------------------------
    # MAIN ANSWER FUNCTION
    # ---------------------------------------------------------

    def answer(self, question, railway_data=None):

        if railway_data is None:
            railway_data = {}

        # If multiple AI results are supplied,
        # use the combined analysis.
        if self.has_multiple_ai_results(railway_data):
            return self.answer_combined(question, railway_data)

        category = self.classify_question(question)

        if category == "root_cause":
            return self.root_cause_analysis(
                railway_data
            )
        
        if category == "delay":
            return self.answer_delay(question, railway_data)

        if category == "congestion":
            return self.answer_congestion(question, railway_data)

        if category == "conflict":
            return self.answer_conflict(question, railway_data)

        if category == "anomaly":
            return self.answer_anomaly(question, railway_data)

        if category == "reroute":
            return self.answer_reroute(question, railway_data)

        if category == "timetable":
            return self.answer_timetable(question, railway_data)

        if category == "signal":
            return self.answer_signal(question, railway_data)

        return self.general_answer()

    # ---------------------------------------------------------
    # DETECT MULTIPLE AI RESULTS
    # ---------------------------------------------------------

    def has_multiple_ai_results(self, data):

        ai_keys = [
            "delay_prediction",
            "congestion_level",
            "conflict",
            "anomaly",
            "reroute_recommended",
            "recommended_signal",
            "timetable"
        ]

        found = 0

        for key in ai_keys:
            if key in data:
                found += 1

        return found >= 2

    # ---------------------------------------------------------
    # COMBINED AI ANALYSIS
    # ---------------------------------------------------------

    def answer_combined(self, question, railway_data):

        train_id = railway_data.get("train_id", "The train")

        findings = []

        # ---------------- DELAY ----------------

        delay = railway_data.get("delay_prediction")

        if delay is not None:
            findings.append(
                f"{train_id} has an AI-predicted delay "
                f"of approximately {delay} minutes."
            )

        # ---------------- CONGESTION ----------------

        congestion = railway_data.get("congestion_level")

        if congestion:
            section = railway_data.get(
                "section",
                "the relevant section"
            )

            confidence = railway_data.get(
                "confidence_percentage"
            )

            text = (
                f"{section} is classified as "
                f"{congestion} congestion."
            )

            if confidence is not None:
                text += (
                    f" Congestion model confidence is "
                    f"{confidence}%."
                )

            findings.append(text)

        # ---------------- CONFLICT ----------------

        conflict = railway_data.get("conflict")

        if conflict is True:

            probability = railway_data.get(
                "conflict_probability"
            )

            text = (
                "The Conflict AI has detected a "
                "potential train conflict."
            )

            if probability is not None:
                text += (
                    f" Estimated conflict probability "
                    f"is {probability}%."
                )

            findings.append(text)

        elif conflict is False:

            findings.append(
                "The Conflict AI does not currently "
                "detect a predicted train conflict."
            )

        # ---------------- ANOMALY ----------------

        anomaly = railway_data.get("anomaly")

        if anomaly is True:

            score = railway_data.get(
                "anomaly_score"
            )

            text = (
                "The Anomaly AI has identified an "
                "unusual railway traffic condition."
            )

            if score is not None:
                text += f" Anomaly score: {score}."

            findings.append(text)

        elif anomaly is False:

            findings.append(
                "The Anomaly AI does not currently "
                "detect an unusual traffic condition."
            )

        # ---------------- REROUTING ----------------

        reroute = railway_data.get(
            "reroute_recommended"
        )

        if reroute is True:

            reason = railway_data.get("reason")
            incident = railway_data.get("incident")

            text = (
                "The Reroute AI recommends an "
                "alternative route."
            )

            if incident:
                text += f" Incident: {incident}."

            if reason:
                text += f" {reason}"

            findings.append(text)

        elif reroute is False:

            reason = railway_data.get("reason")

            text = (
                "The Reroute AI does not recommend "
                "rerouting."
            )

            if reason:
                text += f" {reason}"

            findings.append(text)

        # ---------------- SIGNAL ----------------

        signal = railway_data.get(
            "recommended_signal"
        )

        if signal:

            findings.append(
                f"The Signal AI recommends the "
                f"{signal} signal aspect for the "
                f"supplied conditions."
            )

        # ---------------- FINAL RESPONSE ----------------

        if not findings:

            return (
                "I received railway data, but there "
                "are not enough AI results to perform "
                "a combined analysis."
            )

        response = (
            f"Combined Railway AI analysis for "
            f"{train_id}:\n\n"
        )

        for finding in findings:
            response += "• " + finding + "\n"

        response += (
            "\nThese AI outputs should be considered "
            "together with the simulator's deterministic "
            "safety rules and operator controls."
        )

        return response

    # ---------------------------------------------------------
    # DELAY
    # ---------------------------------------------------------

    def answer_delay(self, question, railway_data):

        if not railway_data:
            return (
                "The Delay AI predicts train delays "
                "using current railway traffic conditions. "
                "Provide the current train data to identify "
                "the predicted delay."
            )

        delay = railway_data.get(
            "delay_prediction"
        )

        train_id = railway_data.get(
            "train_id",
            "The train"
        )

        if delay is not None:
            return (
                f"{train_id} has an AI-predicted delay "
                f"of approximately {delay} minutes. "
                "The prediction should be interpreted "
                "together with current traffic, signal "
                "and conflict conditions."
            )

        return (
            f"I have information about {train_id}, "
            "but a delay prediction is not available "
            "in the supplied data."
        )

    # ---------------------------------------------------------
    # CONGESTION
    # ---------------------------------------------------------

    def answer_congestion(self, question, railway_data):

        if not railway_data:
            return (
                "The Congestion AI analyzes railway "
                "network sections using train count, "
                "speed, track occupancy, headway, "
                "delay and nearby section occupancy."
            )

        section = railway_data.get(
            "section",
            "the section"
        )

        level = railway_data.get(
            "congestion_level"
        )

        confidence = railway_data.get(
            "confidence_percentage"
        )

        if level:

            response = (
                f"{section} is currently classified "
                f"as {level} congestion by the "
                "Network Congestion AI."
            )

            if confidence is not None:
                response += (
                    f" The model confidence is "
                    f"{confidence}%."
                )

            return response

        return (
            f"Congestion information for {section} "
            "is not available in the supplied data."
        )

    # ---------------------------------------------------------
    # CONFLICT
    # ---------------------------------------------------------

    def answer_conflict(self, question, railway_data):

        if not railway_data:
            return (
                "The Conflict AI checks train movement "
                "conditions such as distance, speed, "
                "route interaction and predicted arrival "
                "differences."
            )

        conflict = railway_data.get("conflict")

        probability = railway_data.get(
            "conflict_probability"
        )

        if conflict is True:

            response = (
                "The Conflict AI has detected a "
                "potential train conflict."
            )

            if probability is not None:
                response += (
                    f" Estimated conflict probability: "
                    f"{probability}%."
                )

            return response

        if conflict is False:

            response = (
                "The Conflict AI does not currently "
                "detect a predicted conflict."
            )

            if probability is not None:
                response += (
                    f" Estimated conflict probability: "
                    f"{probability}%."
                )

            return response

        return (
            "A conflict result was not included "
            "in the supplied railway data."
        )

    # ---------------------------------------------------------
    # ANOMALY
    # ---------------------------------------------------------

    def answer_anomaly(self, question, railway_data):

        if not railway_data:
            return (
                "The Anomaly AI looks for unusual "
                "railway traffic conditions using "
                "train speed, distance, occupancy, "
                "signal state and delay."
            )

        anomaly = railway_data.get("anomaly")

        score = railway_data.get(
            "anomaly_score"
        )

        if anomaly is True:

            response = (
                "The Anomaly AI has identified an "
                "unusual traffic condition."
            )

            if score is not None:
                response += (
                    f" Anomaly score: {score}."
                )

            return response

        if anomaly is False:

            response = (
                "The Anomaly AI does not currently "
                "detect an unusual traffic condition."
            )

            if score is not None:
                response += (
                    f" Anomaly score: {score}."
                )

            return response

        return (
            "Anomaly information was not included "
            "in the supplied railway data."
        )

    # ---------------------------------------------------------
    # REROUTE
    # ---------------------------------------------------------

    def answer_reroute(self, question, railway_data):

        if not railway_data:
            return (
                "The Reroute AI recommends an alternative "
                "route only when an actual incident or "
                "route issue is present and the alternative "
                "route satisfies the required safety "
                "conditions."
            )

        recommended = railway_data.get(
            "reroute_recommended"
        )

        reason = railway_data.get("reason")

        incident = railway_data.get("incident")

        if recommended is True:

            response = (
                "The Reroute AI recommends an "
                "alternative route."
            )

            if incident:
                response += (
                    f" Detected incident: {incident}."
                )

            if reason:
                response += f" Reason: {reason}"

            return response

        response = (
            "The Reroute AI does not recommend "
            "rerouting."
        )

        if incident:
            response += (
                f" Incident status: {incident}."
            )

        if reason:
            response += f" Reason: {reason}"

        return response

    # ---------------------------------------------------------
    # TIMETABLE
    # ---------------------------------------------------------

    def answer_timetable(self, question, railway_data):

        if not railway_data:
            return (
                "The Timetable AI uses a Genetic "
                "Algorithm to search for improved "
                "train schedules while considering "
                "platform conflicts, minimum headway, "
                "delay, train priority and platform "
                "constraints."
            )

        timetable = railway_data.get(
            "timetable"
        )

        conflicts = railway_data.get(
            "platform_conflicts"
        )

        headway = railway_data.get(
            "headway_violations"
        )

        if timetable:

            return (
                f"The AI generated an optimized "
                f"timetable for {len(timetable)} trains. "
                f"Platform conflicts: {conflicts}. "
                f"Headway violations: {headway}."
            )

        return (
            "A timetable optimization result was not "
            "included in the supplied railway data."
        )

    # ---------------------------------------------------------
    # SIGNAL
    # ---------------------------------------------------------

    def answer_signal(self, question, railway_data):

        if not railway_data:
            return (
                "The Signal AI uses the current train "
                "distance, speed, track occupancy, "
                "next-train distance, delay and signal "
                "state to recommend a signal aspect."
            )

        signal = railway_data.get(
            "recommended_signal"
        )

        if signal:

            return (
                f"The Signal AI recommends "
                f"{signal} for the supplied conditions. "
                "The recommendation should remain subject "
                "to the simulator's deterministic safety "
                "rules and operator controls."
            )

        return (
            "A signal recommendation was not included "
            "in the supplied railway data."
        )


    # ---------------------------------------------------------
    # ROOT CAUSE ANALYSIS
    # ---------------------------------------------------------

    def root_cause_analysis(self, railway_data):

        causes = []
        observations = []

        train_id = railway_data.get(
            "train_id",
            "The train"
        )

        # -----------------------------------------------------
        # DELAY
        # -----------------------------------------------------

        delay = railway_data.get("delay_prediction")

        if delay is not None:

            if delay >= 15:
                causes.append(
                    f"{train_id} has a significant predicted "
                    f"delay of approximately {delay} minutes."
                )

            elif delay >= 5:
                causes.append(
                    f"{train_id} has a predicted delay of "
                    f"approximately {delay} minutes."
                )

            else:
                observations.append(
                    f"The predicted delay for {train_id} "
                    f"is relatively low at approximately "
                    f"{delay} minutes."
                )

        # -----------------------------------------------------
        # CONGESTION
        # -----------------------------------------------------

        congestion = str(
            railway_data.get(
                "congestion_level",
                ""
            )
        ).upper()

        if congestion == "HIGH":

            causes.append(
                "HIGH network congestion is a major "
                "contributing factor."
            )

        elif congestion == "MEDIUM":

            causes.append(
                "MEDIUM network congestion may be "
                "contributing to the delay."
            )

        elif congestion == "LOW":

            observations.append(
                "The affected section is currently "
                "classified as LOW congestion."
            )

        # -----------------------------------------------------
        # TRACK OCCUPANCY
        # -----------------------------------------------------

        track_occupancy = railway_data.get(
            "track_occupancy"
        )

        if track_occupancy is not None:

            if track_occupancy >= 0.85:

                causes.append(
                    f"Track occupancy is high at "
                    f"{track_occupancy * 100:.1f}%."
                )

            elif track_occupancy >= 0.65:

                causes.append(
                    f"Track occupancy is elevated at "
                    f"{track_occupancy * 100:.1f}%."
                )

        # -----------------------------------------------------
        # NEARBY OCCUPANCY
        # -----------------------------------------------------

        nearby_occupancy = railway_data.get(
            "nearby_occupancy"
        )

        if nearby_occupancy is not None:

            if nearby_occupancy >= 0.85:

                causes.append(
                    f"Nearby sections also have high "
                    f"occupancy at "
                    f"{nearby_occupancy * 100:.1f}%."
                )

            elif nearby_occupancy >= 0.65:

                causes.append(
                    f"Nearby section occupancy is elevated "
                    f"at "
                    f"{nearby_occupancy * 100:.1f}%."
                )

        # -----------------------------------------------------
        # SPEED
        # -----------------------------------------------------

        average_speed = railway_data.get(
            "average_speed"
        )

        if average_speed is not None:

            if average_speed < 25:

                causes.append(
                    f"Average train speed is low at "
                    f"{average_speed}."
                )

            elif average_speed < 40:

                observations.append(
                    f"Average train speed is moderate at "
                    f"{average_speed}."
                )

        # -----------------------------------------------------
        # HEADWAY
        # -----------------------------------------------------

        average_headway = railway_data.get(
            "average_headway"
        )

        if average_headway is not None:

            if average_headway < 5:

                causes.append(
                    f"Average headway is short at "
                    f"{average_headway} minutes, indicating "
                    "closely spaced train movements."
                )

        # -----------------------------------------------------
        # TRAIN COUNT
        # -----------------------------------------------------

        train_count = railway_data.get(
            "train_count"
        )

        if train_count is not None:

            if train_count >= 12:

                causes.append(
                    f"The section currently contains "
                    f"{train_count} trains."
                )

            elif train_count >= 8:

                observations.append(
                    f"The section currently contains "
                    f"{train_count} trains."
                )

        # -----------------------------------------------------
        # CURRENT DELAY
        # -----------------------------------------------------

        current_delay = railway_data.get(
            "current_delay"
        )

        if current_delay is not None:

            if current_delay >= 10:

                causes.append(
                    f"Existing operational delay is "
                    f"{current_delay} minutes."
                )

        # -----------------------------------------------------
        # CONFLICT
        # -----------------------------------------------------

        conflict = railway_data.get(
            "conflict"
        )

        if conflict is True:

            probability = railway_data.get(
                "conflict_probability"
            )

            text = (
                "A predicted train conflict is a "
                "potential contributing factor."
            )

            if probability is not None:

                text += (
                    f" Estimated probability: "
                    f"{probability}%."
                )

            causes.append(text)

        elif conflict is False:

            observations.append(
                "The Conflict AI does not currently "
                "detect a predicted train conflict."
            )

        # -----------------------------------------------------
        # ANOMALY
        # -----------------------------------------------------

        anomaly = railway_data.get(
            "anomaly"
        )

        if anomaly is True:

            causes.append(
                "The Anomaly AI has detected an unusual "
                "traffic condition that requires attention."
            )

        elif anomaly is False:

            observations.append(
                "The Anomaly AI does not currently "
                "detect an unusual traffic condition."
            )

        # -----------------------------------------------------
        # INCIDENT / REROUTING
        # -----------------------------------------------------

        incident = railway_data.get(
            "incident"
        )

        reroute = railway_data.get(
            "reroute_recommended"
        )

        reason = railway_data.get(
            "reason"
        )

        if incident and str(incident).upper() != "NONE":

            causes.append(
                f"An operational incident is reported: "
                f"{incident}."
            )

        elif incident:

            observations.append(
                "No actual route incident is currently "
                "reported."
            )

        if reroute is True:

            causes.append(
                "The Reroute AI recommends an alternative "
                "route because the required incident and "
                "route conditions are satisfied."
            )

        elif reroute is False:

            if reason:

                observations.append(
                    f"Rerouting is not recommended: {reason}"
                )

            else:

                observations.append(
                    "The Reroute AI does not currently "
                    "recommend rerouting."
                )

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        response = (
            f"Root-cause analysis for {train_id}:\n\n"
        )

        if causes:

            response += "Likely contributing factors:\n"

            for cause in causes:

                response += (
                    "• " + cause + "\n"
                )

        else:

            response += (
                "No strong contributing factor was "
                "identified from the supplied data.\n"
            )

        if observations:

            response += (
                "\nOther relevant observations:\n"
            )

            for observation in observations:

                response += (
                    "• " + observation + "\n"
                )

        response += (
            "\nThis is an AI-based analysis of the "
            "supplied simulator data, not a definitive "
            "real-world operational diagnosis."
        )

        return response


    # ---------------------------------------------------------
    # GENERAL
    # ---------------------------------------------------------

    def general_answer(self):

        return (
            "I am the Railway AI Assistant. I can explain "
            "train delays, congestion, conflicts, anomalies, "
            "rerouting recommendations, timetable results "
            "and signal recommendations. Provide the relevant "
            "AI result or current railway data for a specific "
            "explanation."
        )


if __name__ == "__main__":

    assistant = RailwayAssistant()

    print()
    print("=" * 70)
    print("RAILWAY AI ASSISTANT")
    print("=" * 70)
    print()

    print(
        assistant.answer(
            "What is the congestion status?"
        )
    )

    print()
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel

from signal_ai.signal_predictor import SignalAI
signal_ai = SignalAI()

from conflict_ai.conflict_predictor import ConflictAI
conflict_ai = ConflictAI()

from anomaly_ai.anomaly_predictor import AnomalyAI
anomaly_ai = AnomalyAI()

from reroute_ai.reroute_predictor import RerouteAI
reroute_ai = RerouteAI()

from congestion_ai.congestion_predictor import CongestionAI
congestion_ai = CongestionAI()

from timetable_ai.optimizer import TimetableOptimizer
timetable_ai = TimetableOptimizer()

from typing import List

from railway_assistant.assistant import RailwayAssistant
railway_assistant = RailwayAssistant()

from incident_response_ai.incident_response import IncidentResponseAI
incident_response_ai = IncidentResponseAI()

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

from railway_state import railway_state

# --------------------------------------------------
# PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_FILE = BASE_DIR / "model" / "delay_model.pkl"


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

if not MODEL_FILE.exists():

    raise FileNotFoundError(
        f"""
AI model not found.

Expected location:
{MODEL_FILE}

Please run:

python train_model.py

before starting the API.
"""
    )


model = joblib.load(MODEL_FILE)


# --------------------------------------------------
# FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="AI Railway Traffic Management System",
    description="AI-based train delay prediction",
    version="1.0"
)


# --------------------------------------------------
# INPUT MODEL
# --------------------------------------------------

class TrainData(BaseModel):

    current_delay: float

    trains_ahead: int

    track_congestion: float

    signal_wait_time: float

    platform_occupancy: float

    current_speed: float

    distance_to_station: float

    scheduled_travel_time: float

    time_of_day: int


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "AI Railway Traffic Management System is running"
    }


# --------------------------------------------------
# AI DELAY PREDICTION
# --------------------------------------------------

@app.post("/predict-delay")
def predict_delay(data: TrainData):

    input_data = pd.DataFrame(
        [[
            data.current_delay,
            data.trains_ahead,
            data.track_congestion,
            data.signal_wait_time,
            data.platform_occupancy,
            data.current_speed,
            data.distance_to_station,
            data.scheduled_travel_time,
            data.time_of_day
        ]],
        columns=[
            "current_delay",
            "trains_ahead",
            "track_congestion",
            "signal_wait_time",
            "platform_occupancy",
            "current_speed",
            "distance_to_station",
            "scheduled_travel_time",
            "time_of_day"
        ]
    )

    # -----------------------------
    # ACTUAL AI PREDICTION
    # -----------------------------

    prediction = model.predict(input_data)[0]

    prediction = max(
        0,
        float(prediction)
    )


    # -----------------------------
    # RISK LEVEL
    # -----------------------------

    if prediction < 3:

        risk = "LOW"

    elif prediction < 7:

        risk = "MEDIUM"

    else:

        risk = "HIGH"


    # -----------------------------
    # RESPONSE
    # -----------------------------

    return {

        "predicted_additional_delay":
            round(prediction, 2),

        "risk_level":
            risk
    }

class SignalData(BaseModel):

    train_distance: float

    train_speed: float

    track_occupancy: int

    next_train_distance: float

    current_delay: float

    current_signal: int

@app.post("/ai-signal")
def ai_signal(data: SignalData):

    result = signal_ai.predict(

        train_distance=data.train_distance,

        train_speed=data.train_speed,

        track_occupancy=data.track_occupancy,

        next_train_distance=data.next_train_distance,

        current_delay=data.current_delay,

        current_signal=data.current_signal
    )


    return result


class ConflictData(BaseModel):
    train_a_distance: float
    train_a_speed: float

    train_b_distance: float
    train_b_speed: float

    same_junction: int
    conflicting_route: int

    track_occupied: int

    signal_a: int
    signal_b: int

@app.post("/ai-conflict")
def ai_conflict(data: ConflictData):

    result = conflict_ai.predict(
        train_a_distance=data.train_a_distance,
        train_a_speed=data.train_a_speed,

        train_b_distance=data.train_b_distance,
        train_b_speed=data.train_b_speed,

        same_junction=data.same_junction,
        conflicting_route=data.conflicting_route,

        track_occupied=data.track_occupied,

        signal_a=data.signal_a,
        signal_b=data.signal_b
    )

    return result


class AnomalyData(BaseModel):

    train_speed: float
    train_distance: float

    track_occupancy: int
    signal_state: int

    current_delay: float
    next_train_distance: float

    station_distance: float

@app.post("/ai-anomaly")
def ai_anomaly(data: AnomalyData):

    result = anomaly_ai.predict(
        train_speed=data.train_speed,
        train_distance=data.train_distance,

        track_occupancy=data.track_occupancy,
        signal_state=data.signal_state,

        current_delay=data.current_delay,
        next_train_distance=data.next_train_distance,

        station_distance=data.station_distance
    )

    return result


class RerouteData(BaseModel):
    original_route_distance: float
    alternative_route_distance: float
    incident_type: int
    route_blocked: int
    alternative_available: int
    alternative_signal_available: int
    alternative_conflict_risk: float
    alternative_restriction: int
    current_delay: float

@app.post("/ai-reroute")
def ai_reroute(data: RerouteData):
    return reroute_ai.predict(
        original_route_distance=data.original_route_distance,
        alternative_route_distance=data.alternative_route_distance,
        incident_type=data.incident_type,
        route_blocked=data.route_blocked,
        alternative_available=data.alternative_available,
        alternative_signal_available=data.alternative_signal_available,
        alternative_conflict_risk=data.alternative_conflict_risk,
        alternative_restriction=data.alternative_restriction,
        current_delay=data.current_delay
    )

class CongestionData(BaseModel):
    section: str
    train_count: int
    average_speed: float
    track_occupancy: float
    average_headway: float
    current_delay: float
    trains_entering: int
    trains_leaving: int
    nearby_occupancy: float

@app.post("/ai-congestion")
def ai_congestion(data: CongestionData):
    return congestion_ai.predict(
        section=data.section,
        train_count=data.train_count,
        average_speed=data.average_speed,
        track_occupancy=data.track_occupancy,
        average_headway=data.average_headway,
        current_delay=data.current_delay,
        trains_entering=data.trains_entering,
        trains_leaving=data.trains_leaving,
        nearby_occupancy=data.nearby_occupancy
    )

@app.post("/ai-timetable")
def ai_timetable():
    best_solution, score = timetable_ai.optimize()

    return timetable_ai.format_result(
        best_solution,
        score
    )

class TimetableTrain(BaseModel):
    train_id: str
    scheduled_arrival: int
    scheduled_departure: int
    platform: str
    route: str
    priority: int
    current_delay: int


class TimetableOptimizationRequest(BaseModel):
    trains: List[TimetableTrain]

@app.post("/ai-timetable-live")
def ai_timetable_live(data: TimetableOptimizationRequest):

    timetable_ai.trains = [
        train.model_dump()
        for train in data.trains
    ]

    timetable_ai.train_count = len(
        timetable_ai.trains
    )

    best_solution, score = (
        timetable_ai.optimize()
    )

    return timetable_ai.format_result(
        best_solution,
        score
    )

class AssistantRequest(BaseModel):
    question: str
    railway_data: dict = {}
@app.post("/ai-assistant")
def ai_assistant(data: AssistantRequest):

    answer = railway_assistant.answer(
        question=data.question,
        railway_data=data.railway_data
    )

    return {
        "question": data.question,
        "answer": answer
    }

class IncidentResponseRequest(BaseModel):
    railway_data: dict = {}
@app.post("/ai-incident-response")
def ai_incident_response(data: IncidentResponseRequest):

    railway_data = dict(data.railway_data)

    # --------------------------------------------------
    # AUTOMATIC INCIDENT EVENT DETECTION
    # --------------------------------------------------
    # Inspect the actual simulator state so that manual
    # signal restrictions are visible to Incident AI.

    try:

        live_state = railway_state.get_full_state()

        signals = live_state.get("signals", [])
        trains = live_state.get("trains", [])

        for signal in signals:

            status = str(
                signal.get("status", "")
            ).upper()

            mode = str(
                signal.get("mode", "")
            ).upper()

            if status == "RED" and mode == "MANUAL":

                railway_data["incident"] = (
                    "MANUAL SIGNAL RESTRICTION"
                )

                railway_data["section"] = (
                    signal.get(
                        "signal_id",
                        "UNKNOWN"
                    )
                )

                signal_id = signal.get(
                    "signal_id"
                )

                for train in trains:

                    if train.get(
                        "controlling_signal"
                    ) == signal_id:

                        railway_data["train_id"] = (
                            train.get(
                                "train_id",
                                "UNKNOWN"
                            )
                        )

                        break

                break

    except Exception:

        pass

    return incident_response_ai.analyze(
        railway_data
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/dashboard")
def dashboard():

    return {
        "active_trains": 8,
        "signals": 12,
        "anomalies": 1,
        "network_status": "HIGH",

        "ai": {
            "delay": "ACTIVE",
            "signal": "ACTIVE",
            "conflict": "ACTIVE",
            "anomaly": "ACTIVE",
            "congestion": "ACTIVE",
            "reroute": "ACTIVE",
            "incident": "ACTIVE"
        }
    }


# --------------------------------------------------
# RAILWAY SIMULATION STATE
# --------------------------------------------------

@app.get("/railway-state")
def get_railway_state():

    return railway_state.get_full_state()


@app.get("/dashboard-live")
def get_dashboard_live():

    return railway_state.get_dashboard_state()


# --------------------------------------------------
# TRAIN MOVEMENT
# --------------------------------------------------

class TrainMovementRequest(BaseModel):

    train_id: str


@app.post("/train/move")
def move_train(data: TrainMovementRequest):

    return railway_state.move_train(
        data.train_id
    )


# --------------------------------------------------
# MANUAL SIGNAL CONTROL
# --------------------------------------------------

class SignalOverrideRequest(BaseModel):

    signal_id: str
    status: str


@app.post("/manual/signal")
def manual_signal_override(
    data: SignalOverrideRequest
):

    return railway_state.set_signal(
        data.signal_id,
        data.status
    )


# --------------------------------------------------
# MANUAL TRAIN PLATFORM CONTROL
# --------------------------------------------------

class PlatformOverrideRequest(BaseModel):

    train_id: str
    platform_id: str


@app.post("/manual/platform")
def manual_platform_override(
    data: PlatformOverrideRequest
):

    return railway_state.set_train_platform(
        data.train_id,
        data.platform_id
    )

@app.post("/simulation/start")
def start_simulation():
    return railway_state.start_simulation()


@app.post("/simulation/stop")
def stop_simulation():
    return railway_state.stop_simulation()


@app.post("/simulation/tick")
def simulation_tick():
    if not railway_state.simulation_running:
        return {
            "success": False,
            "simulation_running": False,
            "message": "Simulation is currently stopped.",
        }

    return railway_state.simulation_tick()


@app.get("/ai-delay-live/{train_id}")
def live_delay_prediction(train_id: str):

    train = next(
        (
            t for t in railway_state.trains
            if t["train_id"] == train_id
        ),
        None
    )

    if train is None:
        return {
            "success": False,
            "message": f"Train {train_id} not found."
        }

    # --------------------------------------------------
    # Convert current simulation state into the
    # features expected by the trained delay model.
    # --------------------------------------------------

    current_delay = float(train["delay"])
    current_speed = float(train["speed"])

    # Simulator-derived operational values.
    # These are inputs to the existing trained model;
    # the model itself is not being changed.

    trains_ahead = sum(
        1
        for t in railway_state.trains
        if (
            t["train_id"] != train_id
            and t["route"] == train["route"]
            and t["position"] > train["position"]
        )
    )

    track_congestion = min(
        1.0,
        trains_ahead / 5.0
    )

    signal_wait_time = 0.0

    if train["signal"] == "RED":
        signal_wait_time = 5.0
    elif train["signal"] == "DOUBLE YELLOW":
        signal_wait_time = 2.0
    elif train["signal"] == "YELLOW":
        signal_wait_time = 1.0

    platform_occupancy = 0.0

    if train.get("platform"):
        platform = next(
            (
                p for p in railway_state.platforms
                if p["platform_id"] == train["platform"]
            ),
            None
        )

        if platform and platform.get("occupied_by"):
            platform_occupancy = 1.0

    distance_to_station = max(
        0.0,
        100.0 - float(train["position"])
    )

    scheduled_travel_time = 100.0

    # Simple simulator time-of-day value.
    # This keeps the feature compatible with the
    # existing trained model.
    from datetime import datetime
    time_of_day = datetime.now().hour

    input_data = pd.DataFrame(
        [[
            current_delay,
            trains_ahead,
            track_congestion,
            signal_wait_time,
            platform_occupancy,
            current_speed,
            distance_to_station,
            scheduled_travel_time,
            time_of_day
        ]],
        columns=[
            "current_delay",
            "trains_ahead",
            "track_congestion",
            "signal_wait_time",
            "platform_occupancy",
            "current_speed",
            "distance_to_station",
            "scheduled_travel_time",
            "time_of_day"
        ]
    )

    # --------------------------------------------------
    # EXISTING TRAINED AI MODEL
    # --------------------------------------------------

    prediction = model.predict(input_data)[0]

    prediction = max(
        0,
        float(prediction)
    )

    if prediction < 3:
        risk = "LOW"
    elif prediction < 7:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return {
        "success": True,
        "train_id": train_id,

        "current_state": {
            "position": train["position"],
            "speed": train["speed"],
            "current_delay": train["delay"],
            "signal": train["signal"],
            "status": train["status"],
            "route": train["route"],
            "platform": train["platform"]
        },

        "ai_prediction": {
            "predicted_additional_delay": round(prediction, 2),
            "risk_level": risk
        },

        "model_inputs": {
            "trains_ahead": trains_ahead,
            "track_congestion": round(track_congestion, 3),
            "signal_wait_time": signal_wait_time,
            "platform_occupancy": platform_occupancy,
            "distance_to_station": round(
                distance_to_station, 2
            ),
            "scheduled_travel_time": scheduled_travel_time,
            "time_of_day": time_of_day
        }
    }



@app.get("/ai-signal-live/{train_id}")
def live_signal_prediction(train_id: str):

    # --------------------------------------------------
    # FIND TRAIN
    # --------------------------------------------------

    train = next(
        (
            t for t in railway_state.trains
            if t["train_id"] == train_id
        ),
        None
    )

    if train is None:
        return {
            "success": False,
            "message": f"Train {train_id} not found."
        }

    # --------------------------------------------------
    # FIND CONTROLLING SIGNAL
    # --------------------------------------------------

    signal_id = train.get("controlling_signal")

    signal = next(
        (
            s for s in railway_state.signals
            if s["signal_id"] == signal_id
        ),
        None
    )

    if signal is None:
        return {
            "success": False,
            "message": f"Controlling signal {signal_id} not found."
        }

    # --------------------------------------------------
    # CURRENT SIGNAL
    # DQN mapping:
    #
    # 0 = RED
    # 1 = DOUBLE YELLOW
    # 2 = YELLOW
    # 3 = GREEN
    # --------------------------------------------------

    signal_mapping = {
        "RED": 0,
        "DOUBLE YELLOW": 1,
        "YELLOW": 2,
        "GREEN": 3
    }

    current_signal = signal_mapping.get(
        signal["status"],
        0
    )

    # --------------------------------------------------
    # FIND NEXT TRAIN
    #
    # Find the closest train ahead of this train
    # on the same route.
    # --------------------------------------------------

    trains_ahead = [
        t for t in railway_state.trains
        if (
            t["train_id"] != train_id
            and t["route"] == train["route"]
            and t["position"] > train["position"]
        )
    ]

    if trains_ahead:

        next_train = min(
            trains_ahead,
            key=lambda t: t["position"]
        )

        next_train_distance = (
            float(next_train["position"])
            - float(train["position"])
        )

    else:

        next_train_distance = 120.0

    # --------------------------------------------------
    # TRACK OCCUPANCY
    # --------------------------------------------------

    nearby_trains = sum(
        1
        for t in railway_state.trains
        if (
            t["train_id"] != train_id
            and abs(
                float(t["position"])
                - float(train["position"])
            ) < 20
        )
    )

    track_occupancy = min(
        1.0,
        nearby_trains / 3.0
    )

    # --------------------------------------------------
    # RUN EXISTING DQN
    # --------------------------------------------------

    result = signal_ai.predict(

        train_distance=float(train["position"]),

        train_speed=float(train["speed"]),

        track_occupancy=float(track_occupancy),

        next_train_distance=float(
            next_train_distance
        ),

        current_delay=float(train["delay"]),

        current_signal=int(current_signal)
    )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {
        "success": True,

        "train_id": train_id,

        "signal_id": signal_id,

        "current_state": {
            "signal": signal["status"],
            "signal_mode": signal.get(
                "mode",
                "AUTO"
            ),
            "train_position": train["position"],
            "train_speed": train["speed"],
            "train_delay": train["delay"]
        },

        "ai_recommendation": result,

        "ai_inputs": {
            "train_distance": round(
                float(train["position"]),
                2
            ),
            "train_speed": round(
                float(train["speed"]),
                2
            ),
            "track_occupancy": round(
                float(track_occupancy),
                3
            ),
            "next_train_distance": round(
                float(next_train_distance),
                2
            ),
            "current_delay": round(
                float(train["delay"]),
                2
            ),
            "current_signal": current_signal
        }
    }



@app.get("/ai-conflict-live/{train_id}")
def live_conflict_prediction(train_id: str):

    # --------------------------------------------------
    # FIND TRAIN A
    # --------------------------------------------------

    train_a = next(
        (
            t for t in railway_state.trains
            if t["train_id"] == train_id
        ),
        None
    )

    if train_a is None:
        return {
            "success": False,
            "message": f"Train {train_id} not found."
        }

    # --------------------------------------------------
    # FIND THE CLOSEST TRAIN AHEAD
    # --------------------------------------------------

    trains_ahead = [
        t for t in railway_state.trains
        if (
            t["train_id"] != train_id
            and t["position"] > train_a["position"]
        )
    ]

    if not trains_ahead:
        return {
            "success": True,
            "train_id": train_id,
            "conflict_detected": False,
            "message": "No other train ahead to evaluate.",
            "ai_result": None
        }

    train_b = min(
        trains_ahead,
        key=lambda t: t["position"]
    )

    # --------------------------------------------------
    # SIGNAL ENCODING
    #
    # 0 = RED
    # 1 = DOUBLE YELLOW
    # 2 = YELLOW
    # 3 = GREEN
    # --------------------------------------------------

    signal_mapping = {
        "RED": 0,
        "DOUBLE YELLOW": 1,
        "YELLOW": 2,
        "GREEN": 3
    }

    signal_a = signal_mapping.get(
        train_a.get("signal", "RED"),
        0
    )

    signal_b = signal_mapping.get(
        train_b.get("signal", "RED"),
        0
    )

    # --------------------------------------------------
    # ROUTE / JUNCTION CONDITIONS
    # --------------------------------------------------

    same_junction = int(
        train_a["route"] == train_b["route"]
    )

    conflicting_route = int(
        train_a["route"] != train_b["route"]
    )

    # --------------------------------------------------
    # DISTANCE BETWEEN TRAINS
    # --------------------------------------------------

    train_a_distance = float(
        train_a["position"]
    )

    train_b_distance = float(
        train_b["position"]
    )

    distance_between_trains = abs(
        train_b_distance - train_a_distance
    )

    # Consider the track occupied when the trains
    # are within the same simulated operating area.
    track_occupied = int(
        distance_between_trains < 25
    )

    # --------------------------------------------------
    # RUN EXISTING CONFLICT AI
    # --------------------------------------------------

    result = conflict_ai.predict(

        train_a_distance=train_a_distance,
        train_a_speed=float(train_a["speed"]),

        train_b_distance=train_b_distance,
        train_b_speed=float(train_b["speed"]),

        same_junction=same_junction,

        conflicting_route=conflicting_route,

        track_occupied=track_occupied,

        signal_a=signal_a,

        signal_b=signal_b
    )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {
        "success": True,

        "train_a": {
            "train_id": train_a["train_id"],
            "position": train_a["position"],
            "speed": train_a["speed"],
            "route": train_a["route"],
            "signal": train_a["signal"]
        },

        "train_b": {
            "train_id": train_b["train_id"],
            "position": train_b["position"],
            "speed": train_b["speed"],
            "route": train_b["route"],
            "signal": train_b["signal"]
        },

        "relationship": {
            "distance_between_trains": round(
                distance_between_trains,
                2
            ),
            "same_junction": same_junction,
            "conflicting_route": conflicting_route,
            "track_occupied": track_occupied
        },

        "ai_result": result
    }



@app.get("/ai-anomaly-live/{train_id}")
def live_anomaly_prediction(train_id: str):

    # --------------------------------------------------
    # FIND TRAIN
    # --------------------------------------------------

    train = next(
        (
            t for t in railway_state.trains
            if t["train_id"] == train_id
        ),
        None
    )

    if train is None:
        return {
            "success": False,
            "message": f"Train {train_id} not found."
        }

    # --------------------------------------------------
    # SIGNAL ENCODING
    #
    # 0 = RED
    # 1 = DOUBLE YELLOW
    # 2 = YELLOW
    # 3 = GREEN
    # --------------------------------------------------

    signal_mapping = {
        "RED": 0,
        "DOUBLE YELLOW": 1,
        "YELLOW": 2,
        "GREEN": 3
    }

    signal_state = signal_mapping.get(
        train.get("signal", "RED"),
        0
    )

    # --------------------------------------------------
    # FIND NEXT TRAIN
    # --------------------------------------------------

    trains_ahead = [
        t for t in railway_state.trains
        if (
            t["train_id"] != train_id
            and t["route"] == train["route"]
            and t["position"] > train["position"]
        )
    ]

    if trains_ahead:

        next_train = min(
            trains_ahead,
            key=lambda t: t["position"]
        )

        next_train_distance = (
            next_train["position"]
            - train["position"]
        )

    else:
        next_train_distance = 120

    # --------------------------------------------------
    # TRACK OCCUPANCY
    # --------------------------------------------------

    nearby_trains = [
        t for t in railway_state.trains
        if (
            t["train_id"] != train_id
            and t["route"] == train["route"]
            and abs(
                t["position"] - train["position"]
            ) <= 20
        )
    ]

    track_occupancy = min(
        1,
        len(nearby_trains) / 3
    )

    # --------------------------------------------------
    # DISTANCE TO STATION
    #
    # Simulation station/end point = position 100
    # --------------------------------------------------

    station_distance = max(
        0,
        100 - train["position"]
    )

    # --------------------------------------------------
    # RUN EXISTING ANOMALY AI
    # --------------------------------------------------

    result = anomaly_ai.predict(

        train_speed=float(
            train["speed"]
        ),

        train_distance=float(
            train["position"]
        ),

        track_occupancy=int(
            track_occupancy
        ),

        signal_state=signal_state,

        current_delay=float(
            train["delay"]
        ),

        next_train_distance=float(
            next_train_distance
        ),

        station_distance=float(
            station_distance
        )
    )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {
        "success": True,

        "train": {
            "train_id": train["train_id"],
            "position": train["position"],
            "speed": train["speed"],
            "route": train["route"],
            "signal": train["signal"],
            "delay": train["delay"]
        },

        "live_inputs": {
            "train_speed": train["speed"],
            "train_distance": train["position"],
            "track_occupancy": track_occupancy,
            "signal_state": signal_state,
            "current_delay": train["delay"],
            "next_train_distance": next_train_distance,
            "station_distance": station_distance
        },

        "ai_result": result
    }



@app.get("/ai-congestion-live")
def live_congestion_prediction():

    # --------------------------------------------------
    # RAILWAY SECTIONS USED BY THE CONGESTION GNN
    # --------------------------------------------------

    sections = [
        "STATION_A_J1",
        "J1_J2",
        "J2_STATION_B",
        "J1_J3",
        "J3_STATION_C",
        "J2_J4",
        "J4_STATION_D",
        "J3_J5",
        "J5_STATION_E",
        "J4_J6",
        "J6_STATION_F",
        "J5_J7"
    ]

    # --------------------------------------------------
    # MAP SIMULATION ROUTES TO SECTIONS
    #
    # This gives the live simulator a deterministic
    # section assignment while preserving the actual
    # trained Congestion AI.
    # --------------------------------------------------

    route_sections = {
        "A": [
            "STATION_A_J1",
            "J1_J2",
            "J2_STATION_B"
        ],

        "B": [
            "J1_J3",
            "J3_STATION_C",
            "J2_J4",
            "J4_STATION_D"
        ],

        "C": [
            "J3_J5",
            "J5_STATION_E",
            "J4_J6",
            "J6_STATION_F",
            "J5_J7"
        ]
    }

    # --------------------------------------------------
    # ANALYZE EACH SECTION
    # --------------------------------------------------

    section_results = []

    for section in sections:

        # ----------------------------------------------
        # FIND TRAINS ASSOCIATED WITH THIS SECTION
        # ----------------------------------------------

        section_trains = []

        for train in railway_state.trains:

            route = train.get("route")

            if route in route_sections:
                route_section_list = route_sections[route]

                if section in route_section_list:
                    section_trains.append(train)

        # ----------------------------------------------
        # LIVE SECTION STATISTICS
        # ----------------------------------------------

        train_count = len(section_trains)

        if train_count > 0:

            speeds = [
                float(t["speed"])
                for t in section_trains
            ]

            delays = [
                float(t["delay"])
                for t in section_trains
            ]

            average_speed = (
                sum(speeds) / len(speeds)
            )

            current_delay = (
                sum(delays) / len(delays)
            )

        else:

            average_speed = 0.0
            current_delay = 0.0

        # ----------------------------------------------
        # TRACK OCCUPANCY
        # ----------------------------------------------

        track_occupancy = min(
            1.0,
            train_count / 3.0
        )

        # ----------------------------------------------
        # TRAINS ENTERING / LEAVING
        #
        # Approximation based on trains close to
        # the section boundaries in this simulator.
        # ----------------------------------------------

        trains_entering = 0
        trains_leaving = 0

        for train in section_trains:

            position = float(
                train["position"]
            )

            if position < 25:
                trains_entering += 1

            elif position > 75:
                trains_leaving += 1

        # ----------------------------------------------
        # NEARBY OCCUPANCY
        # ----------------------------------------------

        nearby_occupancy = 0.0

        if section_trains:

            total_nearby = 0

            for train in section_trains:

                for other in section_trains:

                    if (
                        train["train_id"]
                        != other["train_id"]
                        and abs(
                            train["position"]
                            - other["position"]
                        ) <= 20
                    ):
                        total_nearby += 1

            possible_pairs = max(
                1,
                train_count * (train_count - 1)
            )

            nearby_occupancy = min(
                1.0,
                total_nearby / possible_pairs
            )

        # ----------------------------------------------
        # AVERAGE HEADWAY
        # ----------------------------------------------

        positions = sorted(
            [
                float(t["position"])
                for t in section_trains
            ]
        )

        if len(positions) >= 2:

            gaps = [
                positions[i + 1] - positions[i]
                for i in range(len(positions) - 1)
            ]

            average_headway = (
                sum(gaps) / len(gaps)
            )

        else:

            average_headway = 120.0

        # ----------------------------------------------
        # RUN EXISTING CONGESTION AI
        # ----------------------------------------------

        ai_result = congestion_ai.predict(

            section=section,

            train_count=train_count,

            average_speed=average_speed,

            track_occupancy=track_occupancy,

            average_headway=average_headway,

            current_delay=current_delay,

            trains_entering=trains_entering,

            trains_leaving=trains_leaving,

            nearby_occupancy=nearby_occupancy
        )

        # ----------------------------------------------
        # STORE RESULT
        # ----------------------------------------------

        section_results.append({

            "section": section,

            "live_data": {
                "train_count": train_count,
                "average_speed": round(
                    average_speed,
                    2
                ),
                "track_occupancy": round(
                    track_occupancy,
                    3
                ),
                "average_headway": round(
                    average_headway,
                    2
                ),
                "current_delay": round(
                    current_delay,
                    2
                ),
                "trains_entering": trains_entering,
                "trains_leaving": trains_leaving,
                "nearby_occupancy": round(
                    nearby_occupancy,
                    3
                )
            },

            "ai_result": ai_result
        })

    # --------------------------------------------------
    # FIND HIGHEST CONGESTION RESULT
    # --------------------------------------------------

    highest_congestion = None

    for result in section_results:

        ai_result = result["ai_result"]

        if highest_congestion is None:
            highest_congestion = result
            continue

        current_level = str(
            ai_result.get(
                "congestion_level",
                ""
            )
        )

        highest_level = str(
            highest_congestion["ai_result"].get(
                "congestion_level",
                ""
            )
        )

        level_value = {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2
        }

        if (
            level_value.get(current_level, 0)
            >
            level_value.get(highest_level, 0)
        ):
            highest_congestion = result

    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    return {

        "success": True,

        "network": {
            "sections_analyzed": len(
                section_results
            ),
            "total_trains": len(
                railway_state.trains
            )
        },

        "highest_congestion_section": (
            highest_congestion["section"]
            if highest_congestion
            else None
        ),

        "highest_congestion_result": (
            highest_congestion["ai_result"]
            if highest_congestion
            else None
        ),

        "sections": section_results
    }



from fastapi import Query

@app.get("/ai-reroute-live/{train_id}")
def ai_reroute_live(
    train_id: str,

    # --------------------------------------------------
    # INCIDENT INFORMATION
    # --------------------------------------------------
    #
    # 0 = NONE
    # 1 = TRACK FAILURE
    # 2 = TRACK BLOCKAGE
    # 3 = SIGNAL FAILURE
    # 4 = MAINTENANCE BLOCK
    # 5 = EMERGENCY / OBSTRUCTION
    #
    incident_type: int = Query(
        0,
        ge=0,
        le=5
    ),

    route_blocked: int = Query(
        0,
        ge=0,
        le=1
    )
):

    # --------------------------------------------------
    # FIND TRAIN
    # --------------------------------------------------

    train = None

    for current_train in railway_state.trains:

        if current_train["train_id"] == train_id:
            train = current_train
            break

    if train is None:

        return {
            "success": False,
            "message": f"Train {train_id} not found."
        }

    # --------------------------------------------------
    # ROUTE INFORMATION
    # --------------------------------------------------

    original_route = train["route"]

    # --------------------------------------------------
    # LIVE ORIGINAL ROUTE DISTANCE
    #
    # In this simulator, position 100 represents the
    # end of the route.
    # --------------------------------------------------

    original_route_distance = max(
        0.0,
        100.0 - float(train["position"])
    )

    # --------------------------------------------------
    # ALTERNATIVE ROUTE
    #
    # Simulator abstraction:
    # each route has another available network path.
    # The alternative is slightly longer.
    # --------------------------------------------------

    alternative_routes = {

        "A": "B",
        "B": "A",
        "C": "B"
    }

    alternative_route = alternative_routes.get(
        original_route
    )

    alternative_available = int(
        alternative_route is not None
    )

    alternative_route_distance = (
        original_route_distance + 20.0
        if alternative_available
        else original_route_distance
    )

    # --------------------------------------------------
    # CHECK SIGNAL AVAILABILITY ON ALTERNATIVE ROUTE
    #
    # A non-RED signal means the alternative route
    # currently has at least one available signal.
    # --------------------------------------------------

    alternative_signal_available = 0

    if alternative_available:

        for signal in railway_state.signals:

            if signal["status"] != "RED":

                alternative_signal_available = 1
                break

    # --------------------------------------------------
    # CALCULATE LIVE ALTERNATIVE CONFLICT RISK
    #
    # Count trains belonging to the alternative route.
    # --------------------------------------------------

    alternative_train_count = 0

    for current_train in railway_state.trains:

        if (
            current_train["route"]
            == alternative_route
        ):

            alternative_train_count += 1

    alternative_conflict_risk = min(
        1.0,
        alternative_train_count / 5.0
    )

    # --------------------------------------------------
    # LIVE ALTERNATIVE RESTRICTION
    #
    # No separate restriction state currently exists
    # in RailwayState, so the simulator currently
    # reports no restriction.
    # --------------------------------------------------

    alternative_restriction = 0

    # --------------------------------------------------
    # CURRENT TRAIN DELAY
    # --------------------------------------------------

    current_delay = float(
        train["delay"]
    )

    # --------------------------------------------------
    # RUN EXISTING REROUTE AI
    # --------------------------------------------------

    ai_result = reroute_ai.predict(

        original_route_distance=(
            original_route_distance
        ),

        alternative_route_distance=(
            alternative_route_distance
        ),

        incident_type=incident_type,

        route_blocked=route_blocked,

        alternative_available=(
            alternative_available
        ),

        alternative_signal_available=(
            alternative_signal_available
        ),

        alternative_conflict_risk=(
            alternative_conflict_risk
        ),

        alternative_restriction=(
            alternative_restriction
        ),

        current_delay=current_delay
    )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {

        "success": True,

        "train": {

            "train_id": train["train_id"],

            "route": original_route,

            "position": train["position"],

            "speed": train["speed"],

            "delay": train["delay"],

            "status": train["status"]
        },

        "live_reroute_inputs": {

            "incident_type": incident_type,

            "route_blocked": route_blocked,

            "original_route": original_route,

            "alternative_route": alternative_route,

            "original_route_distance": round(
                original_route_distance,
                2
            ),

            "alternative_route_distance": round(
                alternative_route_distance,
                2
            ),

            "alternative_available": (
                alternative_available
            ),

            "alternative_signal_available": (
                alternative_signal_available
            ),

            "alternative_conflict_risk": round(
                alternative_conflict_risk,
                3
            ),

            "alternative_restriction": (
                alternative_restriction
            ),

            "current_delay": current_delay
        },

        "ai_result": ai_result,

        "operational_note": (
            "AI provides a rerouting recommendation only. "
            "Final route control remains with the authorized operator."
        )
    }

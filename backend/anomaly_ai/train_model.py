import os

import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "normal_traffic_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "anomaly_model.pkl"
)


# Create model directory

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading normal traffic dataset...")

df = pd.read_csv(DATA_FILE)

print(
    f"Dataset loaded: {len(df)} samples"
)


# --------------------------------------------------
# Select features
# --------------------------------------------------

features = [
    "train_speed",
    "train_distance",
    "track_occupancy",
    "signal_state",
    "current_delay",
    "next_train_distance",
    "station_distance"
]

X = df[features]


# --------------------------------------------------
# Create Isolation Forest
# --------------------------------------------------

print()
print("Training Isolation Forest AI...")


model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)


# --------------------------------------------------
# Train
# --------------------------------------------------

model.fit(X)


# --------------------------------------------------
# Check training data
# --------------------------------------------------

predictions = model.predict(X)


normal_count = sum(
    predictions == 1
)

anomaly_count = sum(
    predictions == -1
)


print()
print("======================================")
print("ANOMALY AI TRAINING RESULTS")
print("======================================")

print(
    f"Normal samples: {normal_count}"
)

print(
    f"Anomaly samples: {anomaly_count}"
)

print(
    f"Anomaly percentage: "
    f"{(anomaly_count / len(predictions)) * 100:.2f}%"
)


# --------------------------------------------------
# Save model
# --------------------------------------------------

joblib.dump(
    model,
    MODEL_FILE
)


print()
print("======================================")
print("AI MODEL SAVED")
print("======================================")

print(
    f"Model: {MODEL_FILE}"
)
import os

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "reroute_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "reroute_model.pkl"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading rerouting dataset...")

df = pd.read_csv(
    DATA_FILE
)

print(
    f"Dataset loaded: {len(df)} samples"
)


# --------------------------------------------------
# Features
# --------------------------------------------------

features = [
    "original_route_distance",
    "alternative_route_distance",
    "incident_type",
    "route_blocked",
    "alternative_available",
    "alternative_signal_available",
    "alternative_conflict_risk",
    "alternative_restriction",
    "current_delay",
    "additional_distance"
]


X = df[features]

y = df["reroute"]


# --------------------------------------------------
# Train / test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples: {len(X_test)}"
)


# --------------------------------------------------
# Create AI model
# --------------------------------------------------

print()
print("Training Rerouting AI...")


model = RandomForestClassifier(
    n_estimators=300,
    max_depth=14,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


# --------------------------------------------------
# Train
# --------------------------------------------------

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# Evaluate
# --------------------------------------------------

predictions = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    predictions
)


print()
print("======================================")
print("REROUTING AI TRAINING RESULTS")
print("======================================")

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)

print()
print("Classification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)

print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
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
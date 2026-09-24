import os

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "conflict_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "conflict_model.pkl"
)


# Create model directory
os.makedirs(MODEL_DIR, exist_ok=True)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset loaded: {len(df)} samples")


# --------------------------------------------------
# Features
# --------------------------------------------------

features = [
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

X = df[features]

y = df["conflict"]


# --------------------------------------------------
# Split dataset
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# --------------------------------------------------
# Create AI model
# --------------------------------------------------

print()
print("Training Random Forest AI...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    class_weight="balanced"
)


# --------------------------------------------------
# Train
# --------------------------------------------------

model.fit(X_train, y_train)


# --------------------------------------------------
# Evaluate
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)


print()
print("======================================")
print("CONFLICT AI TRAINING RESULTS")
print("======================================")

print(f"Accuracy: {accuracy * 100:.2f}%")

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

print(f"Model: {MODEL_FILE}")
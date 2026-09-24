import os
import sys

# Add the backend folder to Python's import path
BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pandas as pd
import torch
import torch.nn.functional as F

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from congestion_ai.gnn_model import CongestionGNN
from congestion_ai.graph import NODES, create_edge_index


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "congestion_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "congestion_gnn.pth"
)


# --------------------------------------------------
# Device
# --------------------------------------------------

device = torch.device("cpu")

print("=" * 60)
print("GNN CONGESTION MODEL TRAINING")
print("=" * 60)

print(f"Device: {device}")
print(f"Dataset: {DATA_FILE}")


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

print(f"\nTotal dataset rows: {len(df)}")


# --------------------------------------------------
# Features
# --------------------------------------------------

FEATURE_COLUMNS = [
    "train_count",
    "average_speed",
    "track_occupancy",
    "average_headway",
    "current_delay",
    "trains_entering",
    "trains_leaving",
    "nearby_occupancy"
]

TARGET_COLUMN = "congestion_level"


# --------------------------------------------------
# Normalize features
# --------------------------------------------------

X = df[FEATURE_COLUMNS].copy()

X["train_count"] = X["train_count"] / 15.0

X["average_speed"] = X["average_speed"] / 120.0

X["track_occupancy"] = X["track_occupancy"]

X["average_headway"] = X["average_headway"] / 20.0

X["current_delay"] = X["current_delay"] / 30.0

X["trains_entering"] = X["trains_entering"] / 6.0

X["trains_leaving"] = X["trains_leaving"] / 6.0

X["nearby_occupancy"] = X["nearby_occupancy"]


# --------------------------------------------------
# Targets
# --------------------------------------------------

y = df[TARGET_COLUMN].values


# --------------------------------------------------
# Map section names to graph nodes
# --------------------------------------------------

df["node_id"] = df["section"].map(NODES)


if df["node_id"].isna().any():

    print("\nERROR: Unknown railway section found.")

    unknown_sections = df[
        df["node_id"].isna()
    ]["section"].unique()

    print(unknown_sections)

    sys.exit(1)


# --------------------------------------------------
# Train / test split
# --------------------------------------------------

indices = list(range(len(df)))

train_indices, test_indices = train_test_split(
    indices,
    test_size=0.20,
    random_state=42,
    stratify=y
)

train_mask = torch.zeros(
    len(df),
    dtype=torch.bool
)

test_mask = torch.zeros(
    len(df),
    dtype=torch.bool
)

train_mask[train_indices] = True

test_mask[test_indices] = True


# --------------------------------------------------
# Convert data to tensors
# --------------------------------------------------

features = torch.tensor(
    X.values,
    dtype=torch.float32
)

labels = torch.tensor(
    y,
    dtype=torch.long
)


# --------------------------------------------------
# Create graph
# --------------------------------------------------

edge_index = create_edge_index()


# --------------------------------------------------
# Create GNN
# --------------------------------------------------

input_features = len(FEATURE_COLUMNS)

hidden_features = 32

output_classes = 3

model = CongestionGNN(
    input_features,
    hidden_features,
    output_classes
).to(device)


# --------------------------------------------------
# Class weights
# --------------------------------------------------

class_counts = torch.bincount(labels)

class_weights = (
    len(labels)
    / (
        len(class_counts)
        * class_counts.float()
    )
)

print("\nClass counts:")

print(
    f"LOW:    {class_counts[0].item()}"
)

print(
    f"MEDIUM: {class_counts[1].item()}"
)

print(
    f"HIGH:   {class_counts[2].item()}"
)

print("\nClass weights:")

print(class_weights)


# --------------------------------------------------
# Optimizer
# --------------------------------------------------

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01,
    weight_decay=5e-4
)


# --------------------------------------------------
# Training
# --------------------------------------------------

epochs = 200

print("\nStarting training...\n")


for epoch in range(1, epochs + 1):

    model.train()

    optimizer.zero_grad()

    output = model(
        features,
        edge_index
    )

    loss = F.cross_entropy(
        output[train_mask],
        labels[train_mask],
        weight=class_weights
    )

    loss.backward()

    optimizer.step()


    # --------------------------------------------------
    # Training accuracy
    # --------------------------------------------------

    predictions = output.argmax(
        dim=1
    )

    train_accuracy = (
        predictions[train_mask]
        == labels[train_mask]
    ).float().mean().item()


    # --------------------------------------------------
    # Test accuracy
    # --------------------------------------------------

    model.eval()

    with torch.no_grad():

        test_output = model(
            features,
            edge_index
        )

        test_predictions = (
            test_output.argmax(dim=1)
        )

        test_accuracy = (
            test_predictions[test_mask]
            == labels[test_mask]
        ).float().mean().item()


    if (
        epoch == 1
        or epoch % 10 == 0
        or epoch == epochs
    ):

        print(
            f"Epoch {epoch:03d}/{epochs} | "
            f"Loss: {loss.item():.4f} | "
            f"Train Accuracy: "
            f"{train_accuracy * 100:.2f}% | "
            f"Test Accuracy: "
            f"{test_accuracy * 100:.2f}%"
        )


# --------------------------------------------------
# Final evaluation
# --------------------------------------------------

model.eval()

with torch.no_grad():

    final_output = model(
        features,
        edge_index
    )

    final_predictions = (
        final_output.argmax(dim=1)
    )


y_true = labels[test_mask].numpy()

y_pred = final_predictions[test_mask].numpy()


print("\n")
print("=" * 60)
print("FINAL GNN EVALUATION")
print("=" * 60)

print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "LOW",
            "MEDIUM",
            "HIGH"
        ]
    )
)


print("Confusion Matrix:")

print(
    confusion_matrix(
        y_true,
        y_pred
    )
)


# --------------------------------------------------
# Save model
# --------------------------------------------------

torch.save(
    model.state_dict(),
    MODEL_FILE
)

print("\n")
print("=" * 60)
print("GNN MODEL SAVED")
print("=" * 60)

print(f"Model: {MODEL_FILE}")
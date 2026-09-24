import os
import random
import pandas as pd


# Number of training examples
NUM_SAMPLES = 10000

data = []


for _ in range(NUM_SAMPLES):

    # Train A
    train_a_distance = random.uniform(100, 1000)
    train_a_speed = random.uniform(20, 120)

    # Train B
    train_b_distance = random.uniform(100, 1000)
    train_b_speed = random.uniform(20, 120)

    # Whether both trains are approaching the same junction
    same_junction = random.randint(0, 1)

    # Whether both trains are on conflicting routes
    conflicting_route = random.randint(0, 1)

    # Track occupancy
    track_occupied = random.randint(0, 1)

    # Signal states
    signal_a = random.randint(0, 3)
    signal_b = random.randint(0, 3)

    # Calculate approximate time to junction
    time_a = train_a_distance / max(train_a_speed, 1)
    time_b = train_b_distance / max(train_b_speed, 1)

    # Difference between arrival times
    arrival_difference = abs(time_a - time_b)

    # ------------------------------------------------
    # Generate conflict label
    # ------------------------------------------------

    conflict = 0

    if (
        same_junction == 1
        and conflicting_route == 1
        and arrival_difference < 15
    ):
        conflict = 1

    if (
        track_occupied == 1
        and same_junction == 1
        and arrival_difference < 10
    ):
        conflict = 1

    # Add some realistic variation
    if random.random() < 0.03:
        conflict = 1 - conflict

    data.append([
        train_a_distance,
        train_a_speed,
        train_b_distance,
        train_b_speed,
        same_junction,
        conflicting_route,
        track_occupied,
        signal_a,
        signal_b,
        time_a,
        time_b,
        arrival_difference,
        conflict
    ])


columns = [
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
    "arrival_difference",
    "conflict"
]


df = pd.DataFrame(data, columns=columns)


# Create data folder
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")

os.makedirs(data_dir, exist_ok=True)


file_path = os.path.join(data_dir, "conflict_data.csv")

df.to_csv(file_path, index=False)


print("======================================")
print("Conflict AI dataset generated")
print("======================================")
print(f"Samples: {len(df)}")
print(f"Saved to: {file_path}")
print()
print(df.head())
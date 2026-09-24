import os
import random
import pandas as pd


NUM_SAMPLES = 10000

data = []


for _ in range(NUM_SAMPLES):

    # Normal railway operating conditions

    train_speed = random.uniform(40, 120)

    train_distance = random.uniform(100, 1000)

    track_occupancy = random.randint(0, 1)

    signal_state = random.randint(0, 3)

    current_delay = random.uniform(0, 15)

    next_train_distance = random.uniform(100, 1000)

    station_distance = random.uniform(500, 5000)

    data.append([
        train_speed,
        train_distance,
        track_occupancy,
        signal_state,
        current_delay,
        next_train_distance,
        station_distance
    ])


columns = [
    "train_speed",
    "train_distance",
    "track_occupancy",
    "signal_state",
    "current_delay",
    "next_train_distance",
    "station_distance"
]


df = pd.DataFrame(
    data,
    columns=columns
)


# Create data directory

base_dir = os.path.dirname(
    os.path.abspath(__file__)
)

data_dir = os.path.join(
    base_dir,
    "data"
)

os.makedirs(
    data_dir,
    exist_ok=True
)


file_path = os.path.join(
    data_dir,
    "normal_traffic_data.csv"
)


df.to_csv(
    file_path,
    index=False
)


print("======================================")
print("ANOMALY AI DATASET GENERATED")
print("======================================")

print(f"Samples: {len(df)}")

print(f"Saved to: {file_path}")

print()

print(df.head())
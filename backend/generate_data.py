import pandas as pd
import numpy as np

np.random.seed(42)

NUM_SAMPLES = 5000

data = {
    "current_delay": np.random.randint(0, 31, NUM_SAMPLES),
    "trains_ahead": np.random.randint(0, 8, NUM_SAMPLES),
    "track_congestion": np.random.randint(0, 101, NUM_SAMPLES),
    "signal_wait_time": np.random.randint(0, 16, NUM_SAMPLES),
    "platform_occupancy": np.random.randint(0, 101, NUM_SAMPLES),
    "current_speed": np.random.randint(20, 121, NUM_SAMPLES),
    "distance_to_station": np.random.randint(1, 101, NUM_SAMPLES),
    "scheduled_travel_time": np.random.randint(5, 61, NUM_SAMPLES),
    "time_of_day": np.random.randint(0, 24, NUM_SAMPLES),
}

df = pd.DataFrame(data)

# Create realistic synthetic delay patterns
df["additional_delay"] = (
    df["current_delay"] * 0.35
    + df["trains_ahead"] * 1.4
    + df["track_congestion"] * 0.08
    + df["signal_wait_time"] * 0.7
    + df["platform_occupancy"] * 0.03
    - df["current_speed"] * 0.015
    + np.random.normal(0, 2, NUM_SAMPLES)
)

# Delays cannot be negative
df["additional_delay"] = df["additional_delay"].clip(lower=0)

df.to_csv("data/train_data.csv", index=False)

print("Dataset created successfully!")
print(df.head())
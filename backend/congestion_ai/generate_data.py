import os
import random
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_DIR, "congestion_data.csv")

# --------------------------------------------------
# Reproducibility
# --------------------------------------------------

random.seed(42)

# --------------------------------------------------
# Railway network sections
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
    "J5_J7",
]

# --------------------------------------------------
# Generate synthetic railway traffic data
# --------------------------------------------------

rows = []

for _ in range(20000):

    section = random.choice(sections)

    train_count = random.randint(0, 15)

    average_speed = random.uniform(20, 120)

    track_occupancy = random.uniform(0.0, 1.0)

    average_headway = random.uniform(1, 20)

    current_delay = random.uniform(0, 30)

    trains_entering = random.randint(0, 6)

    trains_leaving = random.randint(0, 6)

    nearby_occupancy = random.uniform(0.0, 1.0)

    # --------------------------------------------------
    # Calculate congestion score
    # --------------------------------------------------

    congestion_score = (
        train_count * 0.08
        + track_occupancy * 0.35
        + nearby_occupancy * 0.20
        + current_delay * 0.01
        + trains_entering * 0.04
        - trains_leaving * 0.03
        - average_speed * 0.002
        - average_headway * 0.01
    )

    # --------------------------------------------------
    # Convert score into congestion class
    #
    # 0 = LOW
    # 1 = MEDIUM
    # 2 = HIGH
    # --------------------------------------------------

    if congestion_score < 0.35:
        congestion_level = 0

    elif congestion_score < 0.65:
        congestion_level = 1

    else:
        congestion_level = 2

    rows.append({
        "section": section,
        "train_count": train_count,
        "average_speed": round(average_speed, 2),
        "track_occupancy": round(track_occupancy, 3),
        "average_headway": round(average_headway, 2),
        "current_delay": round(current_delay, 2),
        "trains_entering": trains_entering,
        "trains_leaving": trains_leaving,
        "nearby_occupancy": round(nearby_occupancy, 3),
        "congestion_level": congestion_level
    })

# --------------------------------------------------
# Save dataset
# --------------------------------------------------

df = pd.DataFrame(rows)

df.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("CONGESTION DATASET CREATED")
print("=" * 60)

print(f"Dataset: {OUTPUT_FILE}")
print(f"Rows: {len(df)}")

print("\nCongestion distribution:")

print(
    df["congestion_level"]
    .value_counts()
    .sort_index()
    .rename({
        0: "LOW",
        1: "MEDIUM",
        2: "HIGH"
    })
)

print("\nFirst 5 rows:")
print(df.head())
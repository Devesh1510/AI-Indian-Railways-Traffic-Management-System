import os
import random
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)


# ---------------------------------------------------------
# Railway timetable parameters
# ---------------------------------------------------------

TRAINS = [
    "TRAIN_101",
    "TRAIN_102",
    "TRAIN_103",
    "TRAIN_104",
    "TRAIN_105",
    "TRAIN_106",
    "TRAIN_107",
    "TRAIN_108",
]


PLATFORMS = [
    "P1",
    "P2",
    "P3",
    "P4",
]


ROUTES = [
    "ROUTE_A",
    "ROUTE_B",
    "ROUTE_C",
]


# ---------------------------------------------------------
# Generate timetable data
# ---------------------------------------------------------

rows = []


for train_id in TRAINS:

    scheduled_arrival = random.randint(
        5,
        100
    )

    dwell_time = random.randint(
        3,
        8
    )

    scheduled_departure = (
        scheduled_arrival
        + dwell_time
    )

    platform = random.choice(
        PLATFORMS
    )

    # 25% of platforms are fixed.
    # 75% are flexible.

    platform_fixed = random.choice([
        0,
        0,
        0,
        1
    ])

    route = random.choice(
        ROUTES
    )

    priority = random.choice([
        1,
        1,
        1,
        2,
        3
    ])

    delay = random.randint(
        0,
        15
    )

    rows.append({

        "train_id":
            train_id,

        "scheduled_arrival":
            scheduled_arrival,

        "scheduled_departure":
            scheduled_departure,

        "platform":
            platform,

        "platform_fixed":
            platform_fixed,

        "route":
            route,

        "priority":
            priority,

        "current_delay":
            delay

    })


df = pd.DataFrame(
    rows
)


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

output_file = os.path.join(
    DATA_DIR,
    "timetable_data.csv"
)


df.to_csv(
    output_file,
    index=False
)


# ---------------------------------------------------------
# Display result
# ---------------------------------------------------------

print()
print("=" * 70)
print("TIMETABLE DATASET GENERATED")
print("=" * 70)

print()

print(
    f"Number of trains: {len(df)}"
)

print()

print(df.to_string(
    index=False
))

print()

print(
    "Platform fixed distribution:"
)

print(
    df["platform_fixed"].value_counts()
    .sort_index()
)

print()

print(
    "0 = Flexible platform"
)

print(
    "1 = Fixed platform"
)

print()

print(
    f"Saved to:\n{output_file}"
)

print()
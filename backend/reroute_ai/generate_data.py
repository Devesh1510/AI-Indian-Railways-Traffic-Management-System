import os
import random
import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

NUM_SAMPLES = 15000

data = []


# --------------------------------------------------
# Generate incident-based route scenarios
# --------------------------------------------------

for _ in range(NUM_SAMPLES):

    # Route information

    original_route_distance = random.uniform(
        20,
        200
    )

    alternative_route_distance = (
        original_route_distance
        * random.uniform(1.05, 1.80)
    )

    # Actual incident affecting original route

    incident_type = random.randint(
        0,
        5
    )

    # 0 = None
    # 1 = Track failure
    # 2 = Track blockage
    # 3 = Signal failure
    # 4 = Maintenance block
    # 5 = Emergency / obstruction

    # Whether original route is actually blocked

    route_blocked = random.randint(
        0,
        1
    )

    # Whether alternative route is available

    alternative_available = random.randint(
        0,
        1
    )

    # Signal availability on alternative route

    alternative_signal_available = random.randint(
        0,
        1
    )

    # Conflict risk on alternative route

    alternative_conflict_risk = random.uniform(
        0,
        1
    )

    # Existing restrictions

    alternative_restriction = random.randint(
        0,
        1
    )

    # Train delay

    current_delay = random.uniform(
        0,
        60
    )

    # Calculate additional distance

    additional_distance = (
        alternative_route_distance
        - original_route_distance
    )

    # --------------------------------------------------
    # Decide whether rerouting is appropriate
    # --------------------------------------------------

    reroute = 0

    # Rerouting should happen ONLY when
    # an actual issue affects the original route.

    actual_incident = (
        incident_type != 0
    )

    if (
        actual_incident
        and route_blocked == 1
        and alternative_available == 1
        and alternative_signal_available == 1
        and alternative_conflict_risk < 0.60
        and alternative_restriction == 0
    ):
        reroute = 1

    # If there is no actual incident,
    # do NOT reroute merely because of delay.

    if incident_type == 0:
        reroute = 0

    # Add small amount of noise to make
    # the dataset less perfectly deterministic.

    if random.random() < 0.02:
        reroute = 1 - reroute

    data.append([
        original_route_distance,
        alternative_route_distance,
        incident_type,
        route_blocked,
        alternative_available,
        alternative_signal_available,
        alternative_conflict_risk,
        alternative_restriction,
        current_delay,
        additional_distance,
        reroute
    ])


# --------------------------------------------------
# Create DataFrame
# --------------------------------------------------

columns = [
    "original_route_distance",
    "alternative_route_distance",
    "incident_type",
    "route_blocked",
    "alternative_available",
    "alternative_signal_available",
    "alternative_conflict_risk",
    "alternative_restriction",
    "current_delay",
    "additional_distance",
    "reroute"
]


df = pd.DataFrame(
    data,
    columns=columns
)


# --------------------------------------------------
# Save dataset
# --------------------------------------------------

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
    "reroute_data.csv"
)


df.to_csv(
    file_path,
    index=False
)


# --------------------------------------------------
# Output
# --------------------------------------------------

print("======================================")
print("REROUTE AI DATASET GENERATED")
print("======================================")

print(
    f"Samples: {len(df)}"
)

print(
    f"Reroute scenarios: "
    f"{df['reroute'].sum()}"
)

print(
    f"No-reroute scenarios: "
    f"{len(df) - df['reroute'].sum()}"
)

print(
    f"Saved to: {file_path}"
)

print()

print(df.head())
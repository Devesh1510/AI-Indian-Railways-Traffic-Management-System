import os
import random
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "timetable_data.csv"
)


# ============================================================
# GENETIC ALGORITHM PARAMETERS
# ============================================================

POPULATION_SIZE = 80
GENERATIONS = 150

MUTATION_RATE = 0.15
ELITE_COUNT = 10

MIN_HEADWAY = 5

MIN_DWELL = 3
MAX_DWELL = 10

AVAILABLE_PLATFORMS = [
    "P1",
    "P2",
    "P3",
    "P4"
]


# ============================================================
# TIMETABLE OPTIMIZER
# ============================================================

class TimetableOptimizer:

    def __init__(self):

        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(
                f"Timetable dataset not found:\n"
                f"{DATA_FILE}\n\n"
                "Run:\n"
                "python timetable_ai\\generate_data.py"
            )

        self.data = pd.read_csv(DATA_FILE)

        self.trains = self.data.to_dict(
            orient="records"
        )

        self.train_count = len(self.trains)


    # ========================================================
    # CREATE INITIAL SOLUTION
    # ========================================================

    def create_solution(self):

        solution = []

        for train in self.trains:

            arrival = int(
                train["scheduled_arrival"]
            )

            departure = int(
                train["scheduled_departure"]
            )

            dwell = departure - arrival

            solution.append({
                "arrival": arrival,
                "departure": departure,
                "platform": train["platform"],
                "route": train["route"],
                "dwell": dwell
            })

        return solution


    # ========================================================
    # CREATE RANDOM SOLUTION
    # ========================================================

    def create_random_solution(self):

        solution = []

        for train in self.trains:

            original_arrival = int(
                train["scheduled_arrival"]
            )

            # Allow the optimizer to move the train
            # within a reasonable window.

            arrival = original_arrival + random.randint(
                -10,
                10
            )

            arrival = max(
                0,
                arrival
            )

            dwell = random.randint(
                MIN_DWELL,
                MAX_DWELL
            )

            departure = (
                arrival + dwell
            )

            if int(train.get("platform_fixed", 0)) == 1:

                platform = train["platform"]

            else:

                platform = random.choice(
        AVAILABLE_PLATFORMS
    )

            route = train["route"]

            solution.append({
                "arrival": arrival,
                "departure": departure,
                "platform": platform,
                "route": route,
                "dwell": dwell
            })

        return solution


    # ========================================================
    # CHECK PLATFORM CONFLICT
    # ========================================================

    def platform_conflicts(self, solution):

        conflicts = 0

        for i in range(
            self.train_count
        ):

            for j in range(
                i + 1,
                self.train_count
            ):

                train_a = solution[i]
                train_b = solution[j]

                if train_a["platform"] != train_b["platform"]:
                    continue

                a_start = train_a["arrival"]
                a_end = train_a["departure"]

                b_start = train_b["arrival"]
                b_end = train_b["departure"]

                overlap = (
                    a_start < b_end
                    and b_start < a_end
                )

                if overlap:
                    conflicts += 1

        return conflicts

        # ========================================================
    # CHECK INVALID PLATFORM
    # ========================================================

    def invalid_platform_assignments(
        self,
        solution
    ):

        violations = 0

        for train in solution:

            if train["platform"] not in AVAILABLE_PLATFORMS:

                violations += 1

        return violations


    # ========================================================
    # CHECK HEADWAY
    # ========================================================

    def headway_violations(self, solution):

        violations = 0

        for i in range(
            self.train_count
        ):

            for j in range(
                i + 1,
                self.train_count
            ):

                train_a = solution[i]
                train_b = solution[j]

                if train_a["route"] != train_b["route"]:
                    continue

                departure_a = train_a["departure"]
                arrival_b = train_b["arrival"]

                departure_b = train_b["departure"]
                arrival_a = train_a["arrival"]

                # Compare both possible ordering cases.

                if departure_a <= arrival_b:

                    headway = (
                        arrival_b
                        - departure_a
                    )

                    if headway < MIN_HEADWAY:
                        violations += 1

                elif departure_b <= arrival_a:

                    headway = (
                        arrival_a
                        - departure_b
                    )

                    if headway < MIN_HEADWAY:
                        violations += 1

                else:

                    # Both trains overlap.
                    violations += 1

        return violations


    # ========================================================
    # CALCULATE DELAY
    # ========================================================

    def calculate_delay(
        self,
        solution
    ):

        total_delay = 0

        for i, train in enumerate(
            self.trains
        ):

            original_arrival = int(
                train["scheduled_arrival"]
            )

            optimized_arrival = solution[i][
                "arrival"
            ]

            delay = max(
                0,
                optimized_arrival
                - original_arrival
            )

            total_delay += delay

        return total_delay


    # ========================================================
    # CALCULATE SCHEDULE CHANGE
    # ========================================================

    def calculate_schedule_change(
        self,
        solution
    ):

        total_change = 0

        for i, train in enumerate(
            self.trains
        ):

            original_arrival = int(
                train["scheduled_arrival"]
            )

            optimized_arrival = solution[i][
                "arrival"
            ]

            change = abs(
                optimized_arrival
                - original_arrival
            )

            total_change += change

        return total_change


    # ========================================================
    # FITNESS FUNCTION
    # ========================================================

    def fitness(
        self,
        solution
    ):

        platform_conflicts = (
            self.platform_conflicts(
                solution
            )
        )

        invalid_platforms = (
            self.invalid_platform_assignments(
                solution
    )
)

        headway_violations = (
            self.headway_violations(
                solution
            )
        )

        total_delay = (
            self.calculate_delay(
                solution
            )
        )

        schedule_change = (
            self.calculate_schedule_change(
                solution
            )
        )

        # ----------------------------------------------------
        # Priority-aware delay penalty
        # ----------------------------------------------------

        priority_delay_penalty = 0

        for i, train in enumerate(
            self.trains
        ):

            original_arrival = int(
                train["scheduled_arrival"]
            )

            optimized_arrival = int(
                solution[i]["arrival"]
            )

            priority = int(
                train["priority"]
            )


            platform = solution[i]["platform"]

            original_platform = train["platform"]

            if platform != original_platform:

                # Changing the platform of a higher-priority
                # train carries a larger penalty.

                priority_delay_penalty += (
                    priority * 3
                )

            current_delay = int(
                train["current_delay"]
            )

            additional_delay = max(
                0,
                optimized_arrival
                - original_arrival
            )

            # Higher priority = stronger penalty.

            priority_delay_penalty += (
                additional_delay
                * priority
                * 5
            )

            # Give the optimizer an incentive to
            # recover existing delay.

            recovered_delay = min(
                current_delay,
                max(
                    0,
                    original_arrival
                    - optimized_arrival
                )
            )

            priority_delay_penalty -= (
                recovered_delay
                * priority
                * 3
            )

        # ----------------------------------------------------
        # Final fitness score
        # ----------------------------------------------------

        score = 0

        # Hard safety/business constraints.

        score += (
            platform_conflicts * 10000
        )

        score += (
            headway_violations * 10000
        )

        # General delay.

        score += (
            total_delay * 10
        )

        # Priority-aware delay.

        score += (
            priority_delay_penalty
        )

        # Avoid unnecessary timetable changes.

        score += (
            schedule_change * 2
        )

        return score


    # ========================================================
    # TOURNAMENT SELECTION
    # ========================================================

    def select_parent(
        self,
        population
    ):

        tournament_size = 5

        candidates = random.sample(
            population,
            tournament_size
        )

        candidates.sort(
            key=lambda x: x[1]
        )

        return candidates[0][0]


    # ========================================================
    # CROSSOVER
    # ========================================================

    def crossover(
        self,
        parent_a,
        parent_b
    ):

        child = []

        for i in range(
            self.train_count
        ):

            if random.random() < 0.5:

                source = parent_a[i]

            else:

                source = parent_b[i]

            child.append(
                source.copy()
            )

        return child


    # ========================================================
    # MUTATION
    # ========================================================

    def mutate(
        self,
        solution
    ):

        mutated = []

        for gene in solution:

            new_gene = gene.copy()

            if random.random() < MUTATION_RATE:

                # Change arrival time.

                change = random.randint(
                    -5,
                    5
                )

                new_gene["arrival"] = max(
                    0,
                    new_gene["arrival"]
                    + change
                )

                # Recalculate departure.

                new_gene["departure"] = (
                    new_gene["arrival"]
                    + new_gene["dwell"]
                )

            if random.random() < MUTATION_RATE:

    # Only flexible platforms may be changed.

                train_index = len(mutated)

                original_train = self.trains[
                    train_index
                ]

                if int(
                    original_train.get(
                        "platform_fixed",
                        0
                    )
                ) == 0:

                    new_gene["platform"] = random.choice(
                        AVAILABLE_PLATFORMS
        )

            if random.random() < MUTATION_RATE:

                new_gene["dwell"] = random.randint(
                    MIN_DWELL,
                    MAX_DWELL
                )

                new_gene["departure"] = (
                    new_gene["arrival"]
                    + new_gene["dwell"]
                )

            mutated.append(
                new_gene
            )

        return mutated


    # ========================================================
    # OPTIMIZE
    # ========================================================

    def optimize(self):

        population = []

        # ----------------------------------------------------
        # Generate initial population.
        # ----------------------------------------------------

        for _ in range(
            POPULATION_SIZE
        ):

            solution = (
                self.create_random_solution()
            )

            score = self.fitness(
                solution
            )

            population.append(
                (solution, score)
            )


        # ----------------------------------------------------
        # Evolution
        # ----------------------------------------------------

        for generation in range(
            GENERATIONS
        ):

            population.sort(
                key=lambda x: x[1]
            )

            new_population = []

            # Keep best solutions.

            for i in range(
                ELITE_COUNT
            ):

                new_population.append(
                    population[i]
                )


            # Generate remaining solutions.

            while len(
                new_population
            ) < POPULATION_SIZE:

                parent_a = (
                    self.select_parent(
                        population
                    )
                )

                parent_b = (
                    self.select_parent(
                        population
                    )
                )

                child = self.crossover(
                    parent_a,
                    parent_b
                )

                child = self.mutate(
                    child
                )

                child_score = (
                    self.fitness(
                        child
                    )
                )

                new_population.append(
                    (
                        child,
                        child_score
                    )
                )


            population = new_population


        # ----------------------------------------------------
        # Best solution
        # ----------------------------------------------------

        population.sort(
            key=lambda x: x[1]
        )

        best_solution = population[0][0]

        best_score = population[0][1]


        return (
            best_solution,
            best_score
        )


    # ========================================================
    # FORMAT RESULT
    # ========================================================

    def format_result(
        self,
        solution,
        score
    ):

        optimized_timetable = []

        for i, train in enumerate(
            self.trains
        ):

            optimized = solution[i]

            original_arrival = int(
                train["scheduled_arrival"]
            )

            original_departure = int(
                train["scheduled_departure"]
            )

            arrival_change = (
                optimized["arrival"]
                - original_arrival
            )

            departure_change = (
                optimized["departure"]
                - original_departure
            )

            optimized_timetable.append({

                "train_id": train["train_id"],

                "original_arrival":
                    original_arrival,

                "optimized_arrival":
                    optimized["arrival"],

                "arrival_change":
                    arrival_change,

                "original_departure":
                    original_departure,

                "optimized_departure":
                    optimized["departure"],

                "departure_change":
                    departure_change,

                "platform":
    optimized["platform"],

"platform_fixed":
    int(
        train.get(
            "platform_fixed",
            0
        )
    ),

"route":
    optimized["route"],

                "route":
                    optimized["route"],

                "dwell_time":
                    optimized["dwell"]

            })


        return {

            "optimization_method":
                "Genetic Algorithm",

            "fitness_score":
                float(score),

            "platform_conflicts":
                self.platform_conflicts(
                    solution
                ),

            "headway_violations":
                self.headway_violations(
                    solution
                ),

            "total_delay":
                self.calculate_delay(
                    solution
                ),

            "total_schedule_change":
                self.calculate_schedule_change(
                    solution
                ),

            "timetable":
                optimized_timetable

        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AI TIMETABLE OPTIMIZER")
    print("=" * 70)

    optimizer = TimetableOptimizer()

    print()
    print(
        f"Trains loaded: "
        f"{optimizer.train_count}"
    )

    print()
    print(
        "Running Genetic Algorithm..."
    )

    best_solution, score = (
        optimizer.optimize()
    )

    result = optimizer.format_result(
        best_solution,
        score
    )

    print()
    print("=" * 70)
    print("OPTIMIZATION COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Fitness score: "
        f"{result['fitness_score']}"
    )

    print(
        f"Platform conflicts: "
        f"{result['platform_conflicts']}"
    )

    print(
        f"Headway violations: "
        f"{result['headway_violations']}"
    )

    print(
        f"Total delay: "
        f"{result['total_delay']} minutes"
    )

    print(
        f"Schedule change: "
        f"{result['total_schedule_change']} minutes"
    )

    print()
    print("-" * 70)

    for train in result["timetable"]:

        print(
            f"{train['train_id']} | "
            f"Arrival: "
            f"{train['original_arrival']} -> "
            f"{train['optimized_arrival']} | "
            f"Departure: "
            f"{train['original_departure']} -> "
            f"{train['optimized_departure']} | "
            f"Platform: "
            f"{train['platform']} | "
            f"Route: "
            f"{train['route']}"
        )

    print()
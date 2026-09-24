import numpy as np


class RailwaySignalEnvironment:

    def __init__(self):

        # Number of possible signal actions
        #
        # 0 = RED
        # 1 = DOUBLE YELLOW
        # 2 = YELLOW
        # 3 = GREEN

        self.action_space = 4

        # State:
        #
        # train_distance
        # train_speed
        # track_occupancy
        # next_train_distance
        # current_delay
        # current_signal

        self.state_size = 6

        self.max_steps = 200

        self.reset()


    def reset(self):

        self.train_distance = np.random.randint(
            20,
            100
        )

        self.train_speed = np.random.randint(
            20,
            100
        )

        self.track_occupancy = np.random.randint(
            0,
            2
        )

        self.next_train_distance = np.random.randint(
            30,
            120
        )

        self.current_delay = np.random.randint(
            0,
            20
        )

        self.current_signal = np.random.randint(
            0,
            4
        )

        self.steps = 0

        return self._get_state()


    def _get_state(self):

        return np.array(
            [
                self.train_distance / 100,
                self.train_speed / 100,
                self.track_occupancy,
                self.next_train_distance / 120,
                self.current_delay / 20,
                self.current_signal / 3
            ],
            dtype=np.float32
        )


    def step(self, action):

        self.steps += 1

        reward = 0

        # ------------------------------------------------
        # SAFETY RULE
        # ------------------------------------------------

        unsafe_green = (
            action == 3
            and (
                self.track_occupancy == 1
                or self.next_train_distance < 35
            )
        )

        if unsafe_green:

            reward -= 50

        else:

            reward += 5


        # ------------------------------------------------
        # DELAY
        # ------------------------------------------------

        if action == 0:

            # RED → train waits

            self.current_delay += 1

            reward -= 2


        elif action == 1:

            # DOUBLE YELLOW

            self.current_delay += 0.2

            reward += 1


        elif action == 2:

            # YELLOW

            self.current_delay -= 0.5

            reward += 2


        elif action == 3:

            # GREEN

            self.current_delay -= 1

            reward += 4


        # ------------------------------------------------
        # KEEP VALUES VALID
        # ------------------------------------------------

        self.current_delay = max(
            0,
            self.current_delay
        )

        # Simulate movement

        if action != 0:

            self.train_distance -= (
                self.train_speed * 0.05
            )

        else:

            self.train_distance += 1


        # Train reaches next section

        if self.train_distance <= 0:

            self.train_distance = np.random.randint(
                60,
                100
            )

            self.track_occupancy = np.random.randint(
                0,
                2
            )


        # Random traffic changes

        self.next_train_distance += np.random.randint(
            -5,
            6
        )

        self.next_train_distance = np.clip(
            self.next_train_distance,
            20,
            120
        )


        # Update signal

        self.current_signal = action


        # ------------------------------------------------
        # TERMINATION
        # ------------------------------------------------

        done = (
            self.steps >= self.max_steps
        )


        return (
            self._get_state(),
            reward,
            done,
            {}
        )
import torch
import numpy as np

from .dqn import DQN


class SignalAI:

    def __init__(self):

        self.state_size = 6

        self.action_size = 4


        self.model = DQN(
            self.state_size,
            self.action_size
        )


        self.model.load_state_dict(
            torch.load(
                "signal_ai/signal_dqn.pth",
                map_location="cpu"
            )
        )


        self.model.eval()


        self.signal_names = [

            "RED",

            "DOUBLE YELLOW",

            "YELLOW",

            "GREEN"
        ]


    def predict(
        self,
        train_distance,
        train_speed,
        track_occupancy,
        next_train_distance,
        current_delay,
        current_signal
    ):


        state = np.array(
            [

                train_distance / 100,

                train_speed / 100,

                track_occupancy,

                next_train_distance / 120,

                current_delay / 20,

                current_signal / 3

            ],
            dtype=np.float32
        )


        state_tensor = torch.FloatTensor(
            state
        ).unsqueeze(0)


        with torch.no_grad():

            q_values = self.model(
                state_tensor
            )


        action = torch.argmax(
            q_values
        ).item()


        return {

            "recommended_signal":
                self.signal_names[action],

            "q_values":
                q_values[0].tolist(),

            "ai_action":
                action
        }
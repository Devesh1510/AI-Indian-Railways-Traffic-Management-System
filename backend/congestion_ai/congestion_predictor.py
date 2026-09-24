import os
import sys

import torch
import torch.nn.functional as F


# --------------------------------------------------
# Add backend directory to Python path
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.dirname(BASE_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


from congestion_ai.gnn_model import CongestionGNN
from congestion_ai.graph import create_edge_index


class CongestionAI:

    def __init__(self):

        self.model_file = os.path.join(
            BASE_DIR,
            "model",
            "congestion_gnn.pth"
        )

        if not os.path.exists(self.model_file):

            raise FileNotFoundError(
                f"GNN model not found:\n"
                f"{self.model_file}\n\n"
                "Please run:\n"
                "python congestion_ai\\train_model.py"
            )

        # --------------------------------------------------
        # Model configuration
        # --------------------------------------------------

        self.feature_count = 8

        self.hidden_features = 32

        self.output_classes = 3

        # --------------------------------------------------
        # Load model
        # --------------------------------------------------

        self.model = CongestionGNN(
            self.feature_count,
            self.hidden_features,
            self.output_classes
        )

        self.model.load_state_dict(
            torch.load(
                self.model_file,
                map_location="cpu"
            )
        )

        self.model.eval()

        # --------------------------------------------------
        # Railway graph
        # --------------------------------------------------

        self.edge_index = create_edge_index()

        # --------------------------------------------------
        # Node mapping
        # --------------------------------------------------

        self.node_names = [
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
            "J5_J7"
        ]

        self.congestion_names = [
            "LOW",
            "MEDIUM",
            "HIGH"
        ]


    def normalize_features(
        self,
        train_count,
        average_speed,
        track_occupancy,
        average_headway,
        current_delay,
        trains_entering,
        trains_leaving,
        nearby_occupancy
    ):

        return [
            train_count / 15.0,
            average_speed / 120.0,
            track_occupancy,
            average_headway / 20.0,
            current_delay / 30.0,
            trains_entering / 6.0,
            trains_leaving / 6.0,
            nearby_occupancy
        ]


    def predict(
        self,
        section,
        train_count,
        average_speed,
        track_occupancy,
        average_headway,
        current_delay,
        trains_entering,
        trains_leaving,
        nearby_occupancy
    ):

        # --------------------------------------------------
        # Validate section
        # --------------------------------------------------

        if section not in self.node_names:

            raise ValueError(
                f"Unknown railway section: {section}"
            )

        target_node = self.node_names.index(
            section
        )

        # --------------------------------------------------
        # Create features for all graph nodes
        #
        # The target section receives the supplied
        # traffic data.
        #
        # Other nodes receive neutral values.
        # --------------------------------------------------

        features = torch.zeros(
            (len(self.node_names), self.feature_count),
            dtype=torch.float32
        )

        target_features = self.normalize_features(
            train_count,
            average_speed,
            track_occupancy,
            average_headway,
            current_delay,
            trains_entering,
            trains_leaving,
            nearby_occupancy
        )

        features[target_node] = torch.tensor(
            target_features,
            dtype=torch.float32
        )

        # --------------------------------------------------
        # Run GNN
        # --------------------------------------------------

        with torch.no_grad():

            output = self.model(
                features,
                self.edge_index
            )

            probabilities = F.softmax(
                output[target_node],
                dim=0
            )

        predicted_class = int(
            torch.argmax(probabilities).item()
        )

        confidence = float(
            probabilities[predicted_class].item()
        )

        return {
            "section": section,
            "congestion_level": self.congestion_names[
                predicted_class
            ],
            "congestion_class": predicted_class,
            "confidence": round(
                confidence,
                4
            ),
            "confidence_percentage": round(
                confidence * 100,
                2
            ),
            "probabilities": {
                "LOW": round(
                    float(probabilities[0]),
                    4
                ),
                "MEDIUM": round(
                    float(probabilities[1]),
                    4
                ),
                "HIGH": round(
                    float(probabilities[2]),
                    4
                )
            }
        }
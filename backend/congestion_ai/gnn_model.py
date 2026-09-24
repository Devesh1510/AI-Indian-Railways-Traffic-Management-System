import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv


class CongestionGNN(torch.nn.Module):

    def __init__(self, input_features, hidden_features, output_classes):

        super().__init__()

        # First graph convolution layer
        self.conv1 = GCNConv(
            input_features,
            hidden_features
        )

        # Second graph convolution layer
        self.conv2 = GCNConv(
            hidden_features,
            hidden_features
        )

        # Final classification layer
        self.classifier = torch.nn.Linear(
            hidden_features,
            output_classes
        )

    def forward(self, x, edge_index):

        # Graph convolution
        x = self.conv1(
            x,
            edge_index
        )

        x = F.relu(x)

        # Second graph convolution
        x = self.conv2(
            x,
            edge_index
        )

        x = F.relu(x)

        # Predict congestion class
        x = self.classifier(x)

        return x
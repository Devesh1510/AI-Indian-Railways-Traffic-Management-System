import torch

# --------------------------------------------------
# Railway network
#
# Each number represents a railway section/node.
# --------------------------------------------------

NODES = {
    "STATION_A_J1": 0,
    "J1_J2": 1,
    "J2_STATION_B": 2,
    "J1_J3": 3,
    "J3_STATION_C": 4,
    "J2_J4": 5,
    "J4_STATION_D": 6,
    "J3_J5": 7,
    "J5_STATION_E": 8,
    "J4_J6": 9,
    "J6_STATION_F": 10,
    "J5_J7": 11,
}

# --------------------------------------------------
# Connections between railway sections
# --------------------------------------------------

CONNECTIONS = [
    ("STATION_A_J1", "J1_J2"),
    ("J1_J2", "J2_STATION_B"),

    ("STATION_A_J1", "J1_J3"),
    ("J1_J3", "J3_STATION_C"),

    ("J2_J4", "J4_STATION_D"),
    ("J2_J4", "J4_J6"),

    ("J3_J5", "J5_STATION_E"),
    ("J3_J5", "J5_J7"),

    ("J4_J6", "J6_STATION_F"),

    ("J1_J2", "J2_J4"),
    ("J1_J3", "J3_J5"),

    ("J5_J7", "J4_J6"),
]


def create_edge_index():
    """
    Creates the graph connectivity used by the GNN.

    Every railway connection is represented in both
    directions so information can propagate between
    neighbouring sections.
    """

    edges = []

    for source, target in CONNECTIONS:

        source_id = NODES[source]
        target_id = NODES[target]

        # Forward direction
        edges.append([source_id, target_id])

        # Reverse direction
        edges.append([target_id, source_id])

    edge_index = torch.tensor(
        edges,
        dtype=torch.long
    ).t().contiguous()

    return edge_index


if __name__ == "__main__":

    edge_index = create_edge_index()

    print("=" * 60)
    print("RAILWAY GRAPH CREATED")
    print("=" * 60)

    print(f"Number of nodes: {len(NODES)}")
    print(f"Number of connections: {len(CONNECTIONS)}")
    print(f"Graph edges: {edge_index.shape[1]}")

    print("\nNode mapping:")

    for name, node_id in NODES.items():
        print(f"{node_id}: {name}")

    print("\nEdge index:")
    print(edge_index)
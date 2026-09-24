import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from environment import RailwaySignalEnvironment
from dqn import DQN


# ------------------------------------------------
# CONFIGURATION
# ------------------------------------------------

EPISODES = 500

BATCH_SIZE = 64

GAMMA = 0.95

LEARNING_RATE = 0.001

EPSILON = 1.0

EPSILON_MIN = 0.05

EPSILON_DECAY = 0.995


# ------------------------------------------------
# ENVIRONMENT
# ------------------------------------------------

env = RailwaySignalEnvironment()


state_size = env.state_size

action_size = env.action_space


# ------------------------------------------------
# NETWORK
# ------------------------------------------------

policy_net = DQN(
    state_size,
    action_size
)


target_net = DQN(
    state_size,
    action_size
)


target_net.load_state_dict(
    policy_net.state_dict()
)


target_net.eval()


# ------------------------------------------------
# OPTIMIZER
# ------------------------------------------------

optimizer = optim.Adam(
    policy_net.parameters(),
    lr=LEARNING_RATE
)


loss_function = nn.MSELoss()


memory = deque(
    maxlen=10000
)


# ------------------------------------------------
# ACTION
# ------------------------------------------------

def choose_action(
    state,
    epsilon
):

    if random.random() < epsilon:

        return random.randrange(
            action_size
        )


    state_tensor = torch.FloatTensor(
        state
    ).unsqueeze(0)


    with torch.no_grad():

        q_values = policy_net(
            state_tensor
        )


    return torch.argmax(
        q_values
    ).item()


# ------------------------------------------------
# TRAINING
# ------------------------------------------------

def train_step():

    if len(memory) < BATCH_SIZE:

        return


    batch = random.sample(
        memory,
        BATCH_SIZE
    )


    states = torch.FloatTensor(
        [x[0] for x in batch]
    )

    actions = torch.LongTensor(
        [x[1] for x in batch]
    ).unsqueeze(1)

    rewards = torch.FloatTensor(
        [x[2] for x in batch]
    )

    next_states = torch.FloatTensor(
        [x[3] for x in batch]
    )

    dones = torch.FloatTensor(
        [x[4] for x in batch]
    )


    current_q = policy_net(
        states
    ).gather(
        1,
        actions
    ).squeeze()


    with torch.no_grad():

        next_q = target_net(
            next_states
        ).max(
            1
        )[0]


    target_q = rewards + (
        GAMMA
        * next_q
        * (1 - dones)
    )


    loss = loss_function(
        current_q,
        target_q
    )


    optimizer.zero_grad()

    loss.backward()

    optimizer.step()


# ------------------------------------------------
# MAIN TRAINING LOOP
# ------------------------------------------------

print("Starting DQN training...")

for episode in range(
    EPISODES
):

    state = env.reset()

    total_reward = 0


    for step in range(
        env.max_steps
    ):

        action = choose_action(
            state,
            EPSILON
        )


        next_state, reward, done, _ = env.step(
            action
        )


        memory.append(
            (
                state,
                action,
                reward,
                next_state,
                float(done)
            )
        )


        state = next_state

        total_reward += reward


        train_step()


        if done:

            break


    EPSILON = max(
        EPSILON_MIN,
        EPSILON * EPSILON_DECAY
    )


    # Update target network

    if episode % 10 == 0:

        target_net.load_state_dict(
            policy_net.state_dict()
        )


    if episode % 25 == 0:

        print(
            f"Episode {episode} | "
            f"Reward: {total_reward:.2f} | "
            f"Epsilon: {EPSILON:.3f}"
        )


# ------------------------------------------------
# SAVE MODEL
# ------------------------------------------------

torch.save(
    policy_net.state_dict(),
    "signal_ai/signal_dqn.pth"
)


print("\nTraining complete!")

print(
    "AI model saved to:"
)

print(
    "signal_ai/signal_dqn.pth"
)
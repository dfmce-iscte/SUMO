import numpy as np

# Define the environment as a grid world with states and actions
num_states = 4
num_states_dic = {(0,0): 0, (0,1): 1, (1,0): 2, (1,1): 3}
num_actions = 2  # 0:green, 1:red

# Initialize the Q-table with zeros
Q = np.zeros((num_states, num_actions))
rewards = np.array(
    [[0,0,0],
    [0,1,0],
    [1,0,1],
    [1,1,-1],
    [2,0,0],
    [2,1,0],
    [3,0,-1],
    [3,1,1]]
)

# Define parameters
learning_rate = 0.1
discount_factor = 0.9
num_episodes = 1000

# Exploration parameters
epsilon = 0.2  # Epsilon-greedy exploration

# Q-learning algorithm
for episode in range(num_episodes):
    state = 0  # Start in the initial state
    done = False
    total_reward = 0

    while not done:
        # Choose an action using epsilon-greedy strategy
        if np.random.rand() < epsilon:
            action = np.random.choice(num_actions)
        else:
            action = np.argmax(Q[state, :])

        # Perform the selected action and observe the next state and reward
        if action == 0:  # Move up
            next_state = max(state - 1, 0)  # Ensure not going out of bounds
        elif action == 1:  # Move down
            next_state = min(state + 1, num_states - 1)  # Ensure not going out of bounds
        else:  # Left or right
            next_state = state

        reward = -1 if next_state != num_states - 1 else 0  # Reaching the goal state provides reward 0

        # Update the Q-value using the Q-learning update rule
        Q[state, action] = Q[state, action] + learning_rate * (
            reward + discount_factor * np.max(Q[next_state, :]) - Q[state, action]
        )

        total_reward += reward
        state = next_state

        if state == num_states - 1:
            done = True

    if episode % 100 == 0:
        print(f"Episode {episode}: Total Reward = {total_reward}")

# Display the learned Q-table
print("Learned Q-table:")
print(Q)

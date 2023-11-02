import numpy as np

# Define the states and actions
states = [(0, 0), (0, 1), (1, 0), (1, 1)]
actions = [0, 1]  # 0: Green, 1: Red

# Initialize the Q-table with zeros
num_states = len(states)
num_actions = len(actions)
Q = np.zeros((num_states, num_actions))

# Define your reward table (customize this based on your problem)
rewards = np.array([
    [0, 0],
    [0, 0],
    [1, -1],
    [0, 0]
])

# Define the get_next_state function
def get_next_state(current_state, action):
    # Your custom state transition logic here
    # For example, you can use the logic provided in the previous response

    # Example logic:
    if action == 0:  # Green
        if current_state[1] == 1:
            next_state = (1, 0)
        else:
            next_state = (0, 0)
    else:  # Red
        next_state = (current_state[0], current_state[1])

    return next_state

# Hyperparameters
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.2  # Probability of choosing a random action (exploration)

# Number of episodes and steps per episode (customize these)
num_episodes = 1000
max_steps_per_episode = 100

# Q-learning algorithm
for episode in range(num_episodes):
    state = (0, 0)  # Initial state
    total_reward = 0

    for step in range(max_steps_per_episode):
        # Exploration vs. exploitation
        if np.random.rand() < exploration_prob:
            action = np.random.choice(actions)
        else:
            action = np.argmax(Q[state])

        next_state = get_next_state(state, action)  # Get the next state using the custom function

        # Update Q-value using Q-learning update rule
        Q[state][action] = Q[state][action] + learning_rate * (rewards[state][action] + discount_factor * np.max(Q[next_state]) - Q[state][action])

        total_reward += rewards[state][action]
        state = next_state

    # Print the total reward for this episode (to track the learning progress)
    print(f"Episode {episode}: Total Reward = {total_reward}")

# After training, you can use the Q-table to control the traffic light in a real simulation.
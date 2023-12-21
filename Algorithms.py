import numpy as np

gamma = 0.9
epsilon = 0.1
alpha = 0.5
num_episodes = 50
time_limit = 60
nA = 4  # number of choices!!!!!
initial_state = ("L", "L", "L")
states_values = {
    "L": 0,
    "ML": 1,
    "MH": 2,
    "H": 3
}


def print_Q(Q):
    for key, value in Q.items():
        print(key, ':', value)


def create_Q():
    Q = {}
    print("Creating Q-table...")

    with open("States.txt", "r") as f:
        for line in f:
            line_states = line.replace(" ", "").split(",")
            state = (line_states[0], line_states[1], line_states[2].replace("\n", ""))
            Q[state] = np.zeros(nA)
    # print_Q(Q)
    return Q


def epsilon_greedy(Q_state, current_epsilon):
    if np.random.random() > current_epsilon:
        index = np.random.choice(np.where(Q_state == np.max(Q_state))[0])
        # print(f"Best choice: {Q_state}, index: {index}")
        return index
        # return np.random.choice(np.where(Q_state == np.max(Q_state))[0])
    else:
        index = np.random.choice(nA)
        # print(f"Q_state: {Q_state}, index: {index}")
        return index
        # return np.random.choice(nA)


def get_reward(current_state, next_state):
    if current_state == ("L", "L", "L") and current_state == next_state:
        print("No status change but it's still LOW")
        return 50
    elif current_state == ("H", "H", "H") and current_state == next_state:
        print("No status change but it's still HIGH")
        return -50
    diff = sum(states_values[new] - states_values[current] for current, new in zip(current_state, next_state))
    """
    diff can range from -9 (if all parts of the state improve from ‘High’ to ‘Low’) to 9 (if all parts worsen from ‘Low’ to ‘High’).
    """
    if diff < -4:  # High improvement
        reward = 50
    elif diff < 0:  # Improve
        reward = 25
    elif diff == 0:  # No change
        reward = -10
    elif diff < 5:  # Worsen
        reward = -25
    else:  # High worsen
        reward = -50

    return reward


def step(current_state, action, simulation):
    next_state = simulation.execute_new_traffic_light_cycle(action)
    reward = get_reward(current_state, next_state)
    # print(f"State: {current_state}, Next state: {next_state}, Reward: {reward}")
    return next_state, reward


def obtain_policy_from_Q(Q):
    policy = {}
    for state, actions in Q.items():
        policy[state] = np.argmax(actions)
    return policy


def update_probabilities(simulation, time_step):
    if time_step == 30:
        simulation.change_probabilities(0.9, 0.7)
    elif time_step == 45:
        simulation.change_probabilities(0.95, 0.9)


def q_learning(simulation):
    # Here there isn't an exit state.
    current_epsilon = epsilon
    reduction = current_epsilon / num_episodes
    Q = create_Q()
    for n_episode in range(num_episodes):
        print(f"# Episodes: {n_episode}")
        current_state = simulation.get_densities()
        print(f"Initial_state: {current_state}")
        done = False
        time_step = 0
        while not done:
            update_probabilities(simulation, time_step)
            action = epsilon_greedy(Q[current_state], current_epsilon)
            next_state, reward = step(current_state, action, simulation)
            Q[current_state][action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[current_state][action])
            current_state = next_state
            time_step += 1
            done = time_step == time_limit
        if current_epsilon > 0:
            current_epsilon -= reduction
        simulation.remove_all_cars()

    return obtain_policy_from_Q(Q)

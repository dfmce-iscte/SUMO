import numpy as np

gamma = 0.9
epsilon = 0.9
alpha = 0.5
num_episodes = 1000
time_limit = 100
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
            line_states = line.split(",")
            state = (line_states[0], line_states[1], line_states[2].replace("\n", ""))
            Q[state] = np.zeros(nA)
    return Q


def epsilon_greedy(Q_state, current_epsilon):
    if np.random.random() < 1 - current_epsilon:
        return np.argmax(Q_state)
    else:
        return np.random.choice(nA)


# def get_next_state(state, action):
#     # new_state = main.execute_new_traffic_light_cycle(state, action)
#     print("Get next state")
#     return state


def get_reward(current_state, next_state):
    diff = sum(states_values[current] - states_values[new] for current, new in zip(current_state, next_state))
    """
    diff can range from -9 (if all parts of the state improve from ‘High’ to ‘Low’) to 9 (if all parts worsen from ‘Low’ to ‘High’).
    By adding 9 to diff, we shift this range to 0 (best) to 18 (worst).
    Dividing by 4.5 then scales this range to 0 (best) to 4 (worst).
    
    0 - High improve
    1 - Improve
    2 - No change
    3 - Worsen
    4 - High worsen
    """
    # Normalize to 0-10 scale
    diff_scaled = (diff + 9) / 3.6

    if diff_scaled == 4:
        reward = -50
    elif diff_scaled == 3:
        reward = -25
    elif diff_scaled == 2:
        reward = -10
    elif diff_scaled == 1:
        reward = 25
    else:
        reward = 50

    return reward


def step(current_state, action):
    """
        Aqui temos de executar o cycle_time_length do semafore (1min) e depois obter o state atual.
        Temos de criar uma função no python file onde a simulação é executada para executar o step e obter o state obtido.
    """
    # new_state = main.execute_new_traffic_light_cycle(state, action) # Aqui irá fazer um "sleep" de 1min
    # next_state = get_next_state(current_state, action) # Era o que tava na solucao do stor
    next_state = current_state  # Alterar isto!!!!!!!!!!!!
    reward = get_reward(current_state, next_state)
    return next_state, reward


def obtain_policy_from_Q(Q):
    policy = {}
    for state, actions in Q.items():
        policy[state] = np.argmax(actions)
    return policy


def q_learning(num_eps=num_episodes):
    # Here there isn't an exit state.
    current_epsilon = epsilon
    reduction = current_epsilon / num_eps
    Q = create_Q()
    for _ in range(num_eps):
        current_state = initial_state
        done = False
        time_step = 0
        while not done:
            action = epsilon_greedy(Q[current_state], current_epsilon)
            next_state, reward = step(current_state, action)
            Q[current_state][action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[current_state][action])
            current_state = next_state
            time_step += 1
            done = time_step == time_limit
        if current_epsilon > 0:
            current_epsilon -= reduction

    return obtain_policy_from_Q(Q)


def main():
    create_Q()


if __name__ == "__main__":
    main()

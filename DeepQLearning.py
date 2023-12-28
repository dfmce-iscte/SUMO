import numpy as np
from keras import Sequential
from keras.src.layers import Dense
from keras.src.optimizers import Adam


class Agent:
    def __init__(self, agent_state_size, agent_action_size):
        self.n_actions = agent_action_size
        # "lr" : learning rate
        self.lr = 0.001
        # "gamma": discounted factor
        self.gamma = 0.99
        self.exploration_proba = 1.0
        # "exploration_proba_decay": decay of the exploration probability
        self.exploration_proba_decay = 0.05
        # "batch_size": size of experiences we sample to train the DNN
        self.batch_size = 32

        self.memory_buffer = list()
        self.max_memory_buffer = 2000

        self.model = Sequential([
            Dense(units=24, input_dim=agent_state_size, activation='relu'),
            Dense(units=24, activation='relu'),
            Dense(units=agent_action_size, activation='linear')
        ])
        self.model.compile(loss="mse", optimizer=Adam(lr=self.lr))

    # The agent computes the action to perform given a state
    def compute_action(self, current_state):
        if np.random.random() > self.exploration_proba:
            q_values = self.model.predict([current_state])[0]
            index = np.random.choice(np.where(q_values == np.max(q_values))[0])
            # print(f"Best choice: {Q_state}, index: {index}")
            return index
            # return np.random.choice(np.where(Q_state == np.max(Q_state))[0])
        else:
            index = np.random.choice(self.n_actions)
            # print(f"Q_state: {Q_state}, index: {index}")
            return index

    def update_exploration_probability(self):
        self.exploration_proba = self.exploration_proba * np.exp(-self.exploration_proba_decay)
        print(self.exploration_proba)

    def store_episode(self, current_state, action, reward, next_state, done):
        self.memory_buffer.append({
            "current_state": current_state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "done": done
        })
        if len(self.memory_buffer) > self.max_memory_buffer:
            self.memory_buffer.pop(0)

    def train(self):
        # We shuffle the memory buffer and select a batch size of experiences
        np.random.shuffle(self.memory_buffer)
        batch_sample = self.memory_buffer[0:self.batch_size]

        # We iterate over the selected experiences
        for experience in batch_sample:
            q_current_state = self.model.predict(np.array([experience["current_state"]]))
            q_target = experience["reward"]
            if not experience["done"]:
                q_target = q_target + self.gamma * np.max(self.model.predict([experience["next_state"]])[0])
            q_current_state[0][experience["action"]] = q_target
            self.model.fit(np.array([experience["current_state"]]), q_current_state, verbose=0)


state_size = 3
action_size = 4
n_episodes = 100
max_iteration_ep = 60
agent = Agent(state_size, action_size)
total_steps = 0
states_values = {
    "L": 0,
    "ML": 1,
    "MH": 2,
    "H": 3
}


def get_reward(current_state, next_state):
    if current_state == (0, 0, 0) and ('L', 'L', 'L') == next_state:
        print("No status change but it's still LOW")
        return 50
    elif current_state == (3, 3, 3) and ('H', 'H', 'H') == next_state:
        print("No status change but it's still HIGH")
        return -50
    diff = sum(states_values[new] - current for current, new in zip(current_state, next_state))
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


def deep_q_learning(simulation):
    global total_steps

    all_avg_rewards = []

    for n_episode in range(n_episodes):
        print(f"# Episodes: {n_episode}")
        current_state = simulation.get_densities()
        current_state = (states_values[current_state[0]], states_values[current_state[1]],
                         states_values[current_state[2]])
        total_rew_of_episode = 0

        for n_step in range(max_iteration_ep):
            total_steps = total_steps + 1

            action = agent.compute_action(np.array([current_state]))
            next_state, reward = step(current_state, action, simulation)
            next_state = (states_values[next_state[0]], states_values[next_state[1]],
                          states_values[next_state[2]])
            next_state_np = np.array([next_state])

            total_rew_of_episode += reward
            done = n_step == max_iteration_ep - 1

            agent.store_episode(current_state, action, reward, next_state_np, done)

            # if the n_episode is ended, we leave the loop after
            # updating the exploration probability
            if done:
                agent.update_exploration_probability()
                break
            current_state = next_state
        all_avg_rewards.append(total_rew_of_episode / max_iteration_ep)
        # if we have at least batch_size experiences in the memory buffer
        # than we tain our model
        if total_steps >= agent.batch_size:
            agent.train()

        simulation.remove_all_cars()

    policy = {}
    with open("States.txt", "r") as f:
        for line in f:
            line_states = line.replace(" ", "").split(",")
            state = (line_states[0], line_states[1], line_states[2].replace("\n", ""))
            state_int = (states_values[state[0]], states_values[state[1]], states_values[state[2]])
            q_values = agent.model.predict(np.array([state_int]))[0]
            index = np.random.choice(np.where(q_values == np.max(q_values))[0])
            policy[state] = index

    return policy, list(range(n_episodes)), all_avg_rewards

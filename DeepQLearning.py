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
        self.exploration_proba_decay = 0.005
        # "batch_size": size of experiences we sample to train the DNN
        self.batch_size = 32

        # stores only the 2000 last time steps
        self.memory_buffer = list()
        self.max_memory_buffer = 2000

        # The first layer has the same size as a state size
        # The last layer has the size of actions space

        """
        Função de Ativação: A função de ativação ReLU (Rectified Linear Unit) é comumente usada nas camadas ocultas de 
        redes neurais profundas, incluindo aquelas usadas em Deep Q Learning13. A ReLU é popular porque é computacionalmente 
        eficiente e ajuda a mitigar o problema do desaparecimento do gradiente3. Para a camada de saída, a função de ativação 
        depende do tipo de problema de previsão. Em muitos casos de aprendizado por reforço, incluindo Deep Q Learning, 
        uma função de ativação linear é usada na camada de saída.
        """

        self.model = Sequential([
            Dense(units=24, input_dim=agent_state_size, activation='relu'),
            Dense(units=24, activation='relu'),
            Dense(units=agent_action_size, activation='linear')
        ])
        self.model.compile(loss="mse", optimizer=Adam(lr=self.lr))

    # The agent computes the action to perform given a state
    def compute_action(self, current_state):
        # if np.random.uniform(0, 1) < self.exploration_proba:
        #     return np.random.choice(range(self.n_actions))
        # q_values = self.model.predict(current_state)[0]
        # return np.argmax(q_values)
        if np.random.random() < self.exploration_proba:
            q_values = self.model.predict(current_state)[0]
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
            # We compute the Q-values of S_t
            q_current_state = self.model.predict(experience["current_state"])
            # We compute the Q-target using Bellman optimality equation
            q_target = experience["reward"]
            if not experience["done"]:
                q_target = q_target + self.gamma * np.max(self.model.predict(experience["next_state"])[0])
            q_current_state[0][experience["action"]] = q_target
            # train the model
            self.model.fit(experience["current_state"], q_current_state, verbose=0)


# We get the shape of a state and the actions space size
state_size = 64
action_size = 4
# Number of episodes to run
n_episodes = 100
# Max iterations per epiode
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


def deep_q_learning(simulation):
    global total_steps

    for n_episode in range(n_episodes):
        print(f"# Episodes: {n_episode}")
        current_state = simulation.get_densities()

        for n_step in range(max_iteration_ep):
            total_steps = total_steps + 1

            action = agent.compute_action(np.array([current_state]))
            next_state, reward = step(current_state, action, simulation)
            next_state_np = np.array([next_state])

            done = n_step == max_iteration_ep - 1

            # We sotre each experience in the memory buffer
            agent.store_episode(current_state, action, reward, next_state_np, done)

            # if the n_episode is ended, we leave the loop after
            # updating the exploration probability
            if done:
                agent.update_exploration_probability()
                break
            current_state = next_state

        # if the have at least batch_size experiences in the memory buffer
        # than we tain our model
        if total_steps >= agent.batch_size:
            agent.train()

        simulation.remove_all_cars()

import traci
import traci.constants as tc
import random
import numpy as np

# Start the SUMO simulation
sumoBinary = "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe"
sumoCmd = [sumoBinary, "-c", "config_project.sumocfg"]
traci.start(sumoCmd)

# Define the traffic light ID
traffic_light_id = "2"

# Define Q-table and hyperparameters
n_actions = 2  # Actions: switch to red, switch to green
n_states = 4  # Example states: (0, 0) - no cars, (0, 1) - some cars, (1, 0) - green, (1, 1) - red
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.2
Q = np.zeros((n_states, n_actions))

def choose_action(state):
    if random.random() < exploration_prob:
        return random.choice(range(n_actions))
    else:
        return np.argmax(Q[state, :])

# Define simulation parameters
num_steps = 1000  # Number of simulation steps

state = (0, 0)  # Initial state
action = choose_action(state)  # Choose an action for the initial state

for step in range(num_steps):
    traci.simulationStep()

    if step == 0:
        traci.vehicle.add("v1", routeID="r_0", departLane=2, departSpeed=20)
        traci.vehicle.add("v0", routeID="r_0", departLane=0, departSpeed=20)
        traci.vehicle.add("v2", routeID="r_1", departLane=1, departSpeed=20)

    # Collect information about the traffic conditions
    cars_on_highway = traci.edge.getLastStepVehicleNumber("1to2")
    cars_waiting_at_ramp = traci.edge.getLastStepVehicleNumber("entrance")

    # Define the new state based on the collected information
    new_state = (cars_on_highway, cars_waiting_at_ramp)

    # Choose an action for the new state using epsilon-greedy policy
    print(f"New state: {new_state}")
    new_action = choose_action(new_state)

    # Switch the traffic light based on the new action
    if new_action == 0:
        traci.trafficlight.setRedYellowGreenState(traffic_light_id, "GGGG")
    else:
        traci.trafficlight.setRedYellowGreenState(traffic_light_id, "RRRR")

    # Collect the reward based on the change in cars waiting at the ramp
    reward = state[1] - new_state[1]

    # Update the Q-value for the (state, action) pair
    print(f"State: {state}, action: {action}, reward: {reward}, new state: {new_state}, new action: {new_action}")
    Q[state, action] = Q[state, action] + learning_rate * (reward + discount_factor * np.max(Q[new_state]) - Q[state, action])

    # Update the current state and action for the next iteration
    state = new_state
    action = new_action

# End the simulation
print(Q)
traci.close()

import random
import traci
import Algorithms as alg
import DeepQLearning as dql
import matplotlib.pyplot as plt


class Simulation:

    def __init__(self):
        self.before_junction = "E1"
        self.ramp = "E4"
        self.after_junction = "E2"
        self.area_of_before_junction = 0.0
        self.area_of_after_junction = 0.0
        self.area_of_ramp = 0.0
        self.actions_cycles = {
            0: [60, 0, 0],
            1: [40, 5, 15],
            2: [15, 5, 40],
            3: [27, 5, 28]
        }
        self.n_cars = 0
        self.current_sim_step = 0
        self.ramp_probability = 0.95
        self.highway_probability = 0.9

    def change_probabilities(self, ramp_probability, highway_probability):
        self.ramp_probability = ramp_probability
        self.highway_probability = highway_probability
        print(f"Ramp probability: {self.ramp_probability}, Highway probability: {self.highway_probability}")

    def run_sumo(self):
        # sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
        sumoBinary = "/usr/local/bin/sumo"

        sumoBinary = sumoBinary.replace("\\", "/")
        sumoCmd = [sumoBinary, "-c", "final.sumocfg"]

        traci.start(sumoCmd)

        num_lanes_before_junction = traci.edge.getLaneNumber(self.before_junction)
        num_lanes_ramp = traci.edge.getLaneNumber(self.ramp)
        num_lanes_after_junction = traci.edge.getLaneNumber(self.after_junction)

        self.area_of_before_junction = self.calculate_area(self.before_junction, num_lanes_before_junction)

        self.area_of_after_junction = self.calculate_area(self.after_junction, num_lanes_after_junction)

        self.area_of_ramp = self.calculate_area(self.ramp, num_lanes_ramp)

        self.generate_random_vehicles()

    def maybe_create_vehicle(self, percent):
        value = random.random()
        return value >= percent

    def remove_all_cars(self):
        vehicle_ids = traci.vehicle.getIDList()
        for vehicle_id in vehicle_ids:
            traci.vehicle.remove(vehicle_id)

    def calculate_density(self, edge, area):
        sum_of_area_of_cars = 0.0
        vehicles_on_edge = traci.edge.getLastStepVehicleIDs(edge)
        for vehicle_id in vehicles_on_edge:
            vehicle_type = traci.vehicle.getTypeID(vehicle_id)
            sum_of_area_of_cars += (
                    (3.2 * traci.vehicle.getLength(vehicle_id)) + (traci.vehicletype.getMinGap(vehicle_type) * 3.2))
        density = sum_of_area_of_cars / area
        return density

    def generated_scenario3(self):

        types = ["car", "bus", "truck", "motorcycle", "emergency"]
        probabilities = [0.49, 0.15, 0.13, 0.20, 0.03]
        generated_vehicles_highway = random.choices(types, probabilities, k=150)
        generated_vehicles_ramp = random.choices(types, probabilities, k=10)
        for vehicle_type in generated_vehicles_highway:
            lane = random.choice([0, 1, 2])
            depart_speed = random.randint(10, 27)
            traci.vehicle.add("vehicle" + str(self.n_cars), typeID=vehicle_type, routeID="r_0", departLane=lane,
                              departSpeed=depart_speed, departPos=random.randint(0, 1000))
            self.n_cars += 1
        for vehicle_type in generated_vehicles_ramp:
            depart_speed_ramp = random.randint(10, 15)
            traci.vehicle.add("vehicle" + str(self.n_cars), typeID=vehicle_type, routeID="r_1", departLane=0,
                              departSpeed=depart_speed_ramp)
            self.n_cars += 1

    def generate_random_vehicles(self):
        types = ["car", "bus", "truck", "motorcycle", "emergency"]
        probabilities = [0.49, 0.15, 0.13, 0.20, 0.03]
        generated_vehicles = []
        if self.maybe_create_vehicle(self.highway_probability):
            generated_vehicles = random.choices(types, probabilities, k=random.randint(4, 9))
            # generated_vehicles = random.choices(types, probabilities, k=random.randint(2, 5))
        generated_vehicles_ramp = random.choices(types, probabilities,
                                                 k=self.maybe_create_vehicle(self.ramp_probability))

        for vehicle_type in generated_vehicles:
            lane = random.choice([0, 1, 2])
            depart_speed = random.randint(10, 27)
            traci.vehicle.add("vehicle" + str(self.n_cars), typeID=vehicle_type, routeID="r_0", departLane=lane,
                              departSpeed=depart_speed)
            self.n_cars += 1

        for vehicle_type in generated_vehicles_ramp:
            depart_speed_ramp = random.randint(10, 15)
            traci.vehicle.add("vehicle" + str(self.n_cars), typeID=vehicle_type, routeID="r_1", departLane=0,
                              departSpeed=depart_speed_ramp)
            self.n_cars += 1

    def calculate_area(self, road, num_lanes):
        total_width = 0.0

        for lane_index in range(num_lanes):
            lane_id = f"{road}_{lane_index}"
            lane_width = traci.lane.getWidth(lane_id)
            total_width += lane_width

        return total_width * traci.lane.getLength(road + "_0")

    def get_density_category(self, density_value):
        if density_value < 0.05:
            return 'L'
        elif density_value < 0.1:
            return 'ML'
        elif density_value < 0.2:
            return 'MH'
        else:
            return 'H'

    def get_new_phases(self, cycle):
        if cycle[0] == 60:
            phases = [traci.trafficlight.Phase(cycle[0], "GOOO")]
        else:
            phases = [
                traci.trafficlight.Phase(cycle[0], "GOOO"),
                traci.trafficlight.Phase(cycle[1], "yOOO"),
                traci.trafficlight.Phase(cycle[2], "rOOO"),
            ]

        logic = traci.trafficlight.Logic("0", 0, 0, phases)

        traffic_light_id = "J2"
        traci.trafficlight.setProgramLogic(traffic_light_id, logic)

        # Switch to the new program
        traci.trafficlight.setProgram(traffic_light_id, "0")

    def get_densities(self):
        r = self.get_density_category(self.calculate_density(self.ramp, self.area_of_ramp))
        before = self.get_density_category(self.calculate_density(self.before_junction, self.area_of_before_junction))
        after = self.get_density_category(self.calculate_density(self.after_junction, self.area_of_after_junction))

        return r, before, after

    def execute_new_traffic_light_cycle(self, action):
        cycle = self.actions_cycles[action]
        # print(f"GREEN: {cycle[0]}, YELLOW: {cycle[1]}, RED: {cycle[2]}")
        self.get_new_phases(cycle)

        # Execute the traffic light cycle time length (60sec)
        while self.current_sim_step != 60:
            traci.simulationStep()
            self.current_sim_step += 1
            self.generate_random_vehicles()
        self.current_sim_step = 0
        traci.simulationStep()

        return self.get_densities()


def main():
    sim = Simulation()
    sim.run_sumo()
    #policy, episodes, avg_rew = alg.q_learning(sim)
    policy, episodes, avg_rew = dql.deep_q_learning(sim)
    for key, value in policy.items():
        print(f"{key}, action: {value}")
    scenario = 5.1

    #scenario = 3_1
    with open(f"Policies/q_learning_policy_scenario_{scenario}.txt", "w") as f:
        for key, value in policy.items():
            f.write(f"{key}, {sim.actions_cycles[value]}\n")

    fig = plt.figure(figsize=(15, 10))
    ax1 = fig.add_subplot()
    ax1.plot(episodes, avg_rew)
    ax1.set_xlabel("Episodes")
    ax1.set_ylabel("Average Reward")
    fig.savefig(f'Plots/Average_Reward_per_episode-Q-learning_Scenario_{scenario}.png')

    traci.close()


if __name__ == "__main__":
    main()

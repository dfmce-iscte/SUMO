import random
import traci
import Algorithms as alg


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
        self.vehicles_types = ["car", "bus", "truck", "motorcycle", "emergency"]
        self.vehicles_probabilities = [0.49, 0.15, 0.13, 0.20, 0.03]
        self.vehicles_areas = {}
        self.current_sim_step = 0

    def run_sumo(self):
        sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
        sumoBinary = sumoBinary.replace("\\", "/")
        sumoCmd = [sumoBinary, "-c", "final.sumocfg"]

        traci.start(sumoCmd)
        step = 0
        # before_junction = "E1"
        # ramp = "E4"
        # after_junction = "E2"
        # Get the number of lanes for the specified edge

        num_lanes_before_junction = traci.edge.getLaneNumber(self.before_junction)
        num_lanes_ramp = traci.edge.getLaneNumber(self.ramp)
        num_lanes_after_junction = traci.edge.getLaneNumber(self.after_junction)

        self.area_of_before_junction = self.calculate_area(self.before_junction, num_lanes_before_junction)
        print(f"Area of edge {self.before_junction}: {self.area_of_before_junction} meters")

        self.area_of_after_junction = self.calculate_area(self.after_junction, num_lanes_after_junction)
        print(f"Area of edge {self.after_junction}: {self.area_of_after_junction} meters")

        self.area_of_ramp = self.calculate_area(self.ramp, num_lanes_ramp)
        print(f"Area of edge {self.ramp}: {self.area_of_ramp} meters")

        self.vehicles_areas = {
            "car": traci.vehicletype.getMinGap("car") * 3.2 + traci.vehicletype.getLength("car") * 3.2,
            "bus": traci.vehicletype.getMinGap("bus") * 3.2 + traci.vehicletype.getLength("bus") * 3.2,
            "truck": traci.vehicletype.getMinGap("truck") * 3.2 + traci.vehicletype.getLength("truck") * 3.2,
            "motorcycle": traci.vehicletype.getMinGap("motorcycle") * 3.2 + traci.vehicletype.getLength(
                "motorcycle") * 3.2,
            "emergency": traci.vehicletype.getMinGap("emergency") * 3.2 + traci.vehicletype.getLength(
                "emergency") * 3.2,
        }

        self.generate_random_vehicles()

    def maybe_create_vehicle(self, percent):
        value = random.random()
        if value < percent: return 0
        return 1

    def calculate_average_vehicle_area(self):
        # Ensure probabilities and vehicle_sizes have the same length
        if len(self.vehicles_probabilities) != len(self.vehicles_areas):
            raise ValueError("Probabilities and vehicle sizes must have the same length")

        # Calculate the average vehicle area using probabilities and sizes
        average_area = sum(
            self.vehicles_probabilities[i] * self.vehicles_areas[type] for i, type in enumerate(self.vehicles_areas))

        return average_area

    def calculate_max_n_vehicles(self, edge_area):
        return edge_area / self.calculate_average_vehicle_area()

    def calculate_density_by_n_cars(self, edge, edge_area):
        n_vehicles_on_edge = traci.edge.getLastStepVehicleIDs(edge)
        max_cars = self.calculate_max_n_vehicles(edge_area)
        density = len(n_vehicles_on_edge) / max_cars
        print(f"Edge {edge}, max_cars: {max_cars}, n_cars: {len(n_vehicles_on_edge)}, density: {density}")
        return density

    def calculate_density(self, edge, area):
        sum_of_area_of_cars = 0.0
        vehicles_on_edge = traci.edge.getLastStepVehicleIDs(edge)
        for vehicle_id in vehicles_on_edge:
            # lane_id = traci.edge.getLaneID(edge, 0)
            # lane_width = traci.lane.getWidth(lane_id)
            vehicle_type = traci.vehicle.getTypeID(vehicle_id)
            if vehicle_type == "car":
                print(f"Car area: {traci.vehicle.getLength(vehicle_id) * 3.2}")
            sum_of_area_of_cars += (
                        (3.2 * traci.vehicle.getLength(vehicle_id)) + (traci.vehicletype.getMinGap(vehicle_type) * 3.2))
        density = sum_of_area_of_cars / area
        print(f"DENSITY: {density}, Total area: {area}, sum: {sum_of_area_of_cars}")
        return density

    def generate_random_vehicles(self):
        types = ["car", "bus", "truck", "motorcycle", "emergency"]
        probabilities = [0.49, 0.15, 0.13, 0.20, 0.03]
        generated_vehicles = []
        # if self.maybe_create_vehicle(1.0) == 0:
        #     generated_vehicles = random.choices(types, probabilities, k=random.randint(10, 11))
        generated_vehicles = random.choices(types, probabilities, k=30)
        generated_vehicles_ramp = random.choices(types, probabilities, k=self.maybe_create_vehicle(0.6))

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

    def execute_new_traffic_light_cycle(self, action):
        cycle = self.actions_cycles[action]
        print(f"GREEN: {cycle[0]}, YELLOW: {cycle[1]}, RED: {cycle[2]}")
        self.get_new_phases(cycle)

        # Executar os 60seg
        while self.current_sim_step != 60:
            traci.simulationStep()
            self.current_sim_step += 1
            self.generate_random_vehicles()
        self.current_sim_step = 0
        traci.simulationStep()

        r = self.get_density_category(self.calculate_density(self.ramp, self.area_of_ramp))
        before = self.get_density_category(self.calculate_density(self.before_junction, self.area_of_before_junction))
        after = self.get_density_category(self.calculate_density(self.after_junction, self.area_of_after_junction))

        return r, before, after


def main():
    sim = Simulation()
    sim.run_sumo()
    alg.q_learning(sim)

    traci.close()


if __name__ == "__main__":
    main()

import random
import traci


def run_sumo():
    sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
    sumoBinary = sumoBinary.replace("\\", "/")
    sumoCmd = [sumoBinary, "-c", "final.sumocfg"]

    traci.start(sumoCmd)
    step = 0
    before_junction = "E1"
    ramp = "E4"
    after_junction = "E2"
    # Get the number of lanes for the specified edge
    num_lanes_before_junction = traci.edge.getLaneNumber(before_junction)
    num_lanes_ramp = traci.edge.getLaneNumber(ramp)
    num_lanes_after_junction = traci.edge.getLaneNumber(after_junction)

    area_of_before_junction = calculate_area(before_junction, num_lanes_before_junction)
    print(f"Area of edge {before_junction}: {area_of_before_junction} meters")

    area_of_after_junction = calculate_area(ramp,num_lanes_ramp)
    print(f"Area of edge {after_junction}: {area_of_after_junction} meters")

    area_of_ramp = calculate_area(after_junction,num_lanes_after_junction)
    print(f"Area of edge {ramp}: {area_of_ramp} meters")
    while step < 1000:
        before_junction = traci.edge.getLastStepVehicleIDs("E1")
        ramp = traci.edge.getLastStepVehicleIDs("E4")
        after_junction = traci.edge.getLastStepVehicleIDs("E2")
        sumOfAreaOfCarsInBeforeJunction = 0
        sumOfAreaOfCarsInRamp = 0
        sumOfAreaOfcarsAfterJunction = 0
        for x in before_junction:
            # print(traci.vehicle.getTypeID(x))
            # print(traci.vehicle.getWidth(x) * traci.vehicle.getLength(x))
            sumOfAreaOfCarsInBeforeJunction += traci.vehicle.getWidth(x) * traci.vehicle.getLength(x)
        print(f"Density of cars in edge before_junction: {sumOfAreaOfCarsInBeforeJunction / area_of_before_junction}")

        for y in ramp:
            # print(traci.vehicle.getWidth(y) * traci.vehicle.getLength(y))
            sumOfAreaOfCarsInRamp += traci.vehicle.getWidth(y) * traci.vehicle.getLength(y)
        print(f"Density of cars in edge ramp: {sumOfAreaOfCarsInRamp / area_of_ramp}")

        for wyd in after_junction:
            sumOfAreaOfcarsAfterJunction += traci.vehicle.getWidth(wyd) * traci.vehicle.getLength(wyd)
        print(f"Density of cars in edge ramp: {sumOfAreaOfcarsAfterJunction / area_of_after_junction}")

        traci.simulationStep()
        generate_random_vehicles(step)

        step += 1

    traci.close()


def maybeCreateVehicle(percent):
    value = random.random()
    if value < percent: return 0
    return 1


def generate_random_vehicles(step):
    types = ["car", "bus", "truck", "motorcycle", "emergency"]
    probabilities = [0.49, 0.15, 0.13, 0.20, 0.03]
    generated_vehicles = []
    if maybeCreateVehicle(0.6) == 1:
        generated_vehicles = random.choices(types, probabilities, k=random.randint(0, 5))
    generated_vehicles_ramp = random.choices(types, probabilities, k=maybeCreateVehicle(0.9))
    i = 0
    for vehicle_type in generated_vehicles:
        lane = random.choice([0, 1, 2])
        depart_speed = random.randint(10, 20)
        traci.vehicle.add(str(step) + "vehicle" + str(i), typeID=vehicle_type, routeID="r_0", departLane=lane,
                          departSpeed=depart_speed)
        i += 1
    i = 0
    for vehicle_type in generated_vehicles_ramp:
        depart_speed_ramp = random.randint(10, 15)
        traci.vehicle.add(str(step) + "vehicleRamp" + str(i), typeID=vehicle_type, routeID="r_1", departLane=0,
                          departSpeed=depart_speed_ramp)
        i += 1


def calculate_area(road, num_lanes):
    total_width = 0.0

    for lane_index in range(num_lanes):
        lane_id = f"{road}_{lane_index}"
        lane_width = traci.lane.getWidth(lane_id)
        total_width += lane_width

    return total_width * traci.lane.getLength(road + "_0")


def main():
    run_sumo()


if __name__ == "__main__":
    main()

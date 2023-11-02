import random
import traci


def run_sumo():
    sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
    sumoBinary = sumoBinary.replace("\\", "/")
    sumoCmd = [sumoBinary, "-c", "config_project.sumocfg"]

    traci.start(sumoCmd)

    step = 0
    before_junction = "before_junction"
    ramp = "ramp"
    # Get the number of lanes for the specified edge
    num_lanes_before_junction = traci.edge.getLaneNumber(before_junction)
    num_lanes_ramp = traci.edge.getLaneNumber(ramp)

    # Initialize the total width
    total_width_before_junction = 0
    total_width_ramp = 0

    # Iterate through each lane and add its width to the total
    for lane_index in range(num_lanes_before_junction):
        lane_id = f"{before_junction}_{lane_index}"
        lane_width = traci.lane.getWidth(lane_id)
        total_width_before_junction += lane_width

    # Iterate through each lane and add its width to the total
    for lane_index in range(num_lanes_ramp):
        lane_id = f"{ramp}_{lane_index}"
        lane_width = traci.lane.getWidth(lane_id)
        total_width_ramp += lane_width

    area_of_junction = total_width_before_junction * traci.lane.getLength(before_junction + "_0")
    print(f"Area of edge {before_junction}: {area_of_junction} meters")

    area_of_ramp = traci.lane.getLength(ramp + "_0") * total_width_ramp
    print(f"Area of edge {ramp}: {area_of_ramp} meters")
    while step < 1000:
        before_junction = traci.edge.getLastStepVehicleIDs("before_junction")
        ramp = traci.edge.getLastStepVehicleIDs("ramp")
        sumOfAreaOfCarsInBeforeJunction = 0
        sumOfAreaOfCarsInRamp = 0
        for x in before_junction:
            # print(traci.vehicle.getTypeID(x))
            # print(traci.vehicle.getWidth(x) * traci.vehicle.getLength(x))
            sumOfAreaOfCarsInBeforeJunction += traci.vehicle.getWidth(x) * traci.vehicle.getLength(x)
        print(f"Density of cars in edge before_junction: {sumOfAreaOfCarsInBeforeJunction / area_of_junction}")

        for y in ramp:
            # print(traci.vehicle.getWidth(y) * traci.vehicle.getLength(y))
            sumOfAreaOfCarsInRamp += traci.vehicle.getWidth(y) * traci.vehicle.getLength(y)
        print(f"Density of cars in edge ramp: {sumOfAreaOfCarsInRamp / area_of_ramp}")

        traci.simulationStep()
        generate_random_vehicles(step)
        # if step == 0:
        #     traci.vehicle.add("v1", typeID="bus", routeID="r_0", departLane=2, departSpeed=20)
        #     traci.vehicle.add("v0", typeID="car", routeID="r_0", departLane=0, departSpeed=20)
        #     traci.vehicle.add("v2", typeID="motorcycle", routeID="r_0", departLane=1, departSpeed=20)
        #     traci.vehicle.add("v3", typeID="truck", routeID="r_0", departLane=1, departSpeed=20)
        #     traci.vehicle.add("v4", typeID="emergency", routeID="r_0", departLane=1, departSpeed=20)
        # elif step == 10:
        #     traci.vehicle.add("v3", routeID="r_0", departLane=0, departSpeed=20)
        #     traci.vehicle.add("v5", routeID="r_0", departLane=2, departSpeed=20)
        #     traci.vehicle.add("v16", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v17", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v18", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v19", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v20", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v21", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v22", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v23", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v24", routeID="r_0", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v25", routeID="r_0", departLane=0, departSpeed=14)
        # elif step == 17:
        #     traci.vehicle.add("v4", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v7", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v8", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v9", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v10", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v11", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v12", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v13", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v14", routeID="r_1", departLane=0, departSpeed=14)
        #     traci.vehicle.add("v15", routeID="r_1", departLane=0, departSpeed=14)
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


def main():
    run_sumo()


if __name__ == "__main__":
    main()

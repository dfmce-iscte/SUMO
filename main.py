import traci

sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
sumoBinary = sumoBinary.replace("\\", "/")
sumoCmd = [sumoBinary, "-c", "config_project.sumocfg"]

traci.start(sumoCmd)

step = 0
while step < 1000:
    traci.simulationStep()
    if step == 0:
        traci.vehicle.add("v1", routeID="r_0", departLane=2, departSpeed=20)
        traci.vehicle.add("v0", routeID="r_0", departLane=0, departSpeed=20)
        traci.vehicle.add("v2", routeID="r_0", departLane=1, departSpeed=20)
    elif step == 10:
        traci.vehicle.add("v3", routeID="r_0", departLane=0, departSpeed=20)
        traci.vehicle.add("v5", routeID="r_0", departLane=2, departSpeed=20)
    elif step == 17:
        traci.vehicle.add("v4", routeID="r_1", departLane=0, departSpeed=14)
    step += 1

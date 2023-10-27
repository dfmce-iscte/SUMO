import traci

sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
sumoBinary = sumoBinary.replace("\\", "/")
sumoCmd = [sumoBinary, "-c", "config2.sumocfg"]

traci.start(sumoCmd)

step = 0
while step < 1000:
    traci.simulationStep()
    if step == 0:
        traci.vehicle.add(vehID="v0", routeID="r_0", departLane=2, departSpeed=14)
        traci.vehicle.add(vehID="v1", routeID="r_0", departLane=0, departSpeed=14)
        traci.vehicle.add(vehID="v2", routeID="r_0", departLane=1, departSpeed=14)
    elif step == 3:
        traci.vehicle.add(vehID="v3", routeID="r_0", departLane=0, departSpeed=14)
        traci.vehicle.add(vehID="v4", routeID="r_1", departLane=0, departSpeed=14)
    elif step == 1:
        traci.vehicle.add(vehID="v5", routeID="r_1", departLane=0, departSpeed=14)
    step += 1

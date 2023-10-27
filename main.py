import traci
import xml.etree.ElementTree as ET
sumoBinary = "C:\Program Files (x86)\Eclipse\Sumo\\bin\sumo-gui.exe"
sumoBinary = sumoBinary.replace("\\", "/")
sumoCmd = [sumoBinary, "-c", "config_project.sumocfg"]

traci.start(sumoCmd)
traffic_light_id = "tl1"
E5_0="E5_0"
E5_1="E5_1"
E5_2="E5_2"
e2_0_0=":2_0_0"
e2_1_0=":2_1_0"
e2_1_1=":2_1_1"
e2_1_2=":2_1_2"
e1to2_0="1to2_0"
e1to2_1="1to2_1"
e1to2_2="1to2_2"

# Load the SUMO network XML file
tree = ET.parse("project_network.net.xml")
root = tree.getroot()


step = 0
while step < 1000:
    vehicles = traci.vehicle.getIDList()
    p1 = [v for v in vehicles if traci.vehicle.getLaneID(v) == E5_0]
    p2 = [v for v in vehicles if traci.vehicle.getLaneID(v) == E5_1]
    p3 = [v for v in vehicles if traci.vehicle.getLaneID(v) == E5_2]
    p4 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e2_0_0]
    p5 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e2_1_0]
    p6 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e2_1_1]
    p7 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e2_1_2]
    p8 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e1to2_0]
    p9 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e1to2_1]
    p10 = [v for v in vehicles if traci.vehicle.getLaneID(v) == e1to2_2]

    # Print the detected vehicles
    print(f"Vehicles on E5_0: {len(p1)}")
    print(f"Vehicles on E5_1: {len(p2)}")
    print(f"Vehicles on E5_2: {len(p3)}")
    print(f"Vehicles on e2_0_0: {len(p4)}")
    print(f"Vehicles on e2_1_0: {len(p5)}")
    print(f"Vehicles on e2_1_1: {len(p6)}")
    print(f"Vehicles on e2_1_2: {len(p7)}")
    print(f"Vehicles on e1to2_0: {len(p8)}")
    print(f"Vehicles on e1to2_1: {len(p9)}")
    print(f"Vehicles on e1to2_2: {len(p10)}")

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

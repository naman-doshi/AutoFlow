"""
This script executes the backend simulation.

A virtual landscape is firstly generated, and a population of vehicle agents with random 
starting positions and destinations are spawned.

The population is then cloned and distributed with AutoFlow at a specified percentage.
The modified population groups are tested within the same landscape for statistical analysis.

All routing data are produced and sent to the Unity frontend via AutoFlow Bridge.
"""

#================ IMPORTS ================
from AutoFlow import *
# from TestHelper import *

from copy import deepcopy
#=========================================

#================ INPUTS =================
LANDSCAPE_SIZE = (20, 20)
LANDSCAPE_FEATURES = [
    (LandPlotDescriptor((2, 2), (1, 1)), 5)
]
LANDSCAPE_FILLER = LandPlotDescriptor((2, 2), (2, 2), None)
# VEHICLE_COUNT = 20 # size constraint in place, may not always fit
#=========================================


# ===============================================================================================
# Landscape Generation
# ===============================================================================================

# Generate virtual landscape
landscape = Landscape(*LANDSCAPE_SIZE)
#landscape.generate_new_landscape(desiredFeatures=LANDSCAPE_FEATURES, filler=LANDSCAPE_FILLER)
landscape.generate_new_landscape()

# There must be at least one road within the map area
assert len(landscape.intersections) > 4

# # Check for overlapping roads
# for roadA in landscape.roads:
#     for roadB in landscape.roads:
#         if roadA != roadB:
#             if doIntersect(
#                 Point(*roadA.startPosReal),
#                 Point(*roadA.endPosReal),
#                 Point(*roadB.startPosReal),
#                 Point(*roadB.endPosReal)
#             ):
#                 print(roadA.startPosReal, roadA.endPosReal)
#                 print(roadB.startPosReal, roadB.endPosReal)
#                 raise Exception("Roads overlap, this should not occur")

# Compute average road speed for all roads within map area
road_speeds = 0
road_count = 0
for road in landscape.roads:
    if (
        1 <= road.start[0] <= landscape.xSize and 1 <= road.start[1] <= landscape.ySize or 
        1 <= road.end[0] <= landscape.xSize and 1 <= road.end[1] <= landscape.ySize
    ):
        road_speeds += road.speedLimit
        road_count += 1
AVERAGE_ROAD_SPEED = road_speeds / road_count
AVERAGE_ROAD_SPEED_MPS = AVERAGE_ROAD_SPEED * 1000 / 3600


# ===============================================================================================
# Spawn Vehicle Agents
# ===============================================================================================

# Create two pools of available starting coordinates (as every road segment has a pair of opposite roads)
available_coordinates = [
    [
        (i, j) for i in range(1, landscape.xSize+1) for j in range(1, landscape.ySize+1) 
        if (i, j) in landscape.coordToRoad
    ],
    [
        (i, j) for i in range(1, landscape.xSize+1) for j in range(1, landscape.ySize+1) 
        if (i, j) in landscape.coordToRoad
    ]
]

# Generate a valid vehicle count
MAX_VEHICLE_COUNT = len(available_coordinates[0]) * 2
print(MAX_VEHICLE_COUNT)
VEHICLE_COUNT = randint(int(MAX_VEHICLE_COUNT*9/10), MAX_VEHICLE_COUNT)

# Check that the vehicle count does not exceed the maximum allowed vehicle count
assert VEHICLE_COUNT <= len(available_coordinates[0]) * 2

# Array storing all vehicle agents
vehicles: list[Vehicle] = []

# Determine EV distribution
EV_percentage = randint(10, 20) # based on real world data
EV_count = EV_percentage * VEHICLE_COUNT // 100 # number of EVs to spawn

current_index = 0

# Spawn EVs
while current_index < EV_count:
    # if current_index in marked_indexes:
    #     vehicle = ElectricVehicle(useAutoFlow=True)
    #     autoflow_vehicles.append(vehicle)
    # else:
    #     vehicle = ElectricVehicle(useAutoFlow=False)
    #     selfish_vehicles.append(vehicle)
    vehicle = ElectricVehicle()
    vehicles.append(vehicle)
    current_index += 1

# Spawn conventional vehicles
while current_index < VEHICLE_COUNT:
    # if current_index in marked_indexes:
    #     vehicle = ConventionalVehicle(useAutoFlow=True)
    #     autoflow_vehicles.append(vehicle)
    # else:
    #     vehicle = ConventionalVehicle(useAutoFlow=False)
    #     selfish_vehicles.append(vehicle)
    vehicle = ConventionalVehicle()
    vehicles.append(vehicle)
    current_index += 1

# Assign random starting coordinates to all vehicles
for vehicle in vehicles:

    # Select random pool
    poolID = randint(0, 1) 
    if len(available_coordinates[poolID]) == 0:
        poolID = 1-poolID # if current pool is used up, use the other pool

    # Select random coordinate from pool, and determine which road it is on
    coordIndex = randint(0, len(available_coordinates[poolID]) - 1) 
    coord = available_coordinates[poolID][coordIndex]
    road = landscape.coordToRoad[coord][poolID]

    vehicle.setLocation(road, road.positionTable[coord]) # set vehicle's starting location

    available_coordinates[poolID].pop(coordIndex) # remove assigned coord from pool

for road in landscape.roads: # sort vehicle stacks, cars at the front are at the front/start of the deque
    road.vehicleStack = deque(sorted(road.vehicleStack, key = lambda vehicle: vehicle.position, reverse=True))

# Create two pools of available destination coordinates (as every road segment has a pair of opposite roads)
available_coordinates = [
    [
        (i, j) for i in range(1, landscape.xSize+1) for j in range(1, landscape.ySize+1) 
        if (i, j) in landscape.coordToRoad
    ],
    [
        (i, j) for i in range(1, landscape.xSize+1) for j in range(1, landscape.ySize+1) 
        if (i, j) in landscape.coordToRoad
    ]
]

# Assign random destination coordinates to all vehicles
for vehicle in vehicles:

    # Select random pool
    poolID = randint(0, 1) 
    if len(available_coordinates[poolID]) == 0:
        poolID = 1-poolID # if current pool is used up, use the other pool

    # Select random coordinate from pool, and determine which road it is on
    coordIndex = randint(0, len(available_coordinates[poolID]) - 1) 
    coord = available_coordinates[poolID][coordIndex]
    road = landscape.coordToRoad[coord][poolID]

    vehicle.setDestination(road, road.positionTable[coord]) # set vehicle's destination location

    available_coordinates[poolID].pop(coordIndex) # remove assigned coord from pool


# ===============================================================================================
# AutoFlow Distribution Functions
# ===============================================================================================

def modify_population(original_vehicle_population: list[Vehicle], autoflow_percentage: float) -> tuple[list[Vehicle], list[Vehicle]]:
    """
    Returns a new population of vehicle agents with a specified percentage having the AutoFlow routing system.
    A tuple of two lists of vehicles are returned: (selfish_vehicles, autoflow_vehicles).
    """

    # Make a deepcopy of the original vehicle population for modification
    vehicle_population: list[Vehicle] = deepcopy(original_vehicle_population)
    #vehicle_population = original_vehicle_population

    # Determine AutoFlow distribution
    marked_indexes = set(sample([i for i in range(VEHICLE_COUNT)], VEHICLE_COUNT * autoflow_percentage // 100))

    # Initiate vehicle lists
    selfish_vehicles: list[Vehicle] = []
    autoflow_vehicles: list[Vehicle] = []

    # Distribute AutoFlow & categorise vehicles
    for i in range(VEHICLE_COUNT):
        if i in marked_indexes:
            vehicle_population[i].routingSystem = Vehicle.routingSystems[1] # switch to AutoFlow
            autoflow_vehicles.append(vehicle_population[i])
        else:
            selfish_vehicles.append(vehicle_population[i])

    # Return vehicle lists
    return (selfish_vehicles, autoflow_vehicles)


# ===============================================================================================
# Testing
# ===============================================================================================

#print(vehicles)
print(VEHICLE_COUNT)
print()


# 100% Selfish
selfish_vehicles, autoflow_vehicles = modify_population(vehicles, 0)
selfish_vehicle_routes, autoflow_vehicle_routes = computeRoutes(selfish_vehicles, autoflow_vehicles, landscape, AVERAGE_ROAD_SPEED_MPS)
routes1 = deepcopy(selfish_vehicle_routes)

# for vehicle in selfish_vehicles:
#     #print(vehicle.road, vehicle.road.positionTable, vehicle.position)
#     #print(vehicle.destinationPosition, vehicle.destinationRoad)
#     print(
#         getRealPositionOnRoad(vehicle.road, vehicle.position),
#         getRealPositionOnRoad(vehicle.destinationRoad, vehicle.destinationPosition)
#     )
    
print(len(selfish_vehicle_routes))
print()

# for route in selfish_vehicle_routes:
#     print(route)
#     print()

# 100% AutoFlow
selfish_vehicles, autoflow_vehicles = modify_population(vehicles, 100)
selfish_vehicle_routes, autoflow_vehicle_routes = computeRoutes(selfish_vehicles, autoflow_vehicles, landscape, AVERAGE_ROAD_SPEED_MPS)
routes2 = deepcopy(autoflow_vehicle_routes)

# for vehicle in autoflow_vehicles:
#     #print(vehicle.road, vehicle.road.positionTable, vehicle.position)
#     #print(vehicle.destinationPosition, vehicle.destinationRoad)
#     print(
#         getRealPositionOnRoad(vehicle.road, vehicle.position),
#         getRealPositionOnRoad(vehicle.destinationRoad, vehicle.destinationPosition)
#     )

print(len(autoflow_vehicle_routes))
print()

# for route in autoflow_vehicle_routes:
#     print(route)
#     print()


# Function for calculating total distance of a route
def calculate_total_distance(route: list[tuple[float, float]]):
    total_distance = 0
    current_pos = route[0]
    for i in range(1, len(route)):
        total_distance += euclideanDistance(current_pos, route[i])
        current_pos = route[i]
    return total_distance

# Compare routes
# for i in range(VEHICLE_COUNT):
#     if routes1[i] != routes2[i]:
#         print(f"""
# Start: {getRealPositionOnRoad(vehicles[i].road, vehicles[i].position)},
# Destination: {getRealPositionOnRoad(vehicles[i].destinationRoad, vehicles[i].destinationPosition)}"""
#         )
#         print(routes1[i])
#         print(f"Route1 distance: {calculate_total_distance(routes1[i])}")
#         print(routes2[i])
#         print(f"Route2 distance: {calculate_total_distance(routes2[i])}")
#         print()
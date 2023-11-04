"""
This script contains the multiple route computing algorithms, including:
- selfish A* routing algorithm
- AutoFlow collaborative routing algorithm
"""


#================ IMPORTS ================
from LandscapeComponents import *
from VehicleAgents import *

from random import sample
from heapq import *
from math import ceil
from ML import pred
#=========================================

# ===============================================================================================
# Helper Functions
# ===============================================================================================

def getRealPositionOnRoad(road: Road, position: float) -> tuple[float, float]:
    """
    Calculates the real 2D position given road and a normalised position.
    """
    if road.direction == "N":
        return (road.startPosReal[0], road.startPosReal[1] + road.length * position)
    elif road.direction == "S":
        return (road.startPosReal[0], road.startPosReal[1] - road.length * position)
    elif road.direction == "E":
        return (road.startPosReal[0] + road.length * position, road.startPosReal[1])
    elif road.direction == "W":
        return (road.startPosReal[0] - road.length * position, road.startPosReal[1])
    
def euclideanDistance(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    """
    Calculates the euclidean distance between two positions.
    The unit of measurement is metres.
    """
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5


# ===============================================================================================
# Main Functions
# ===============================================================================================

def computeRoutes(selfish_vehicles: list[Vehicle], autoflow_vehicles: list[Vehicle], landscape: Landscape, AVERAGE_ROAD_SPEED_MPS: float) -> tuple[list[tuple[tuple[float, float], int]]]:
    """
    Compute the routes for selfish vehicles first, then AutoFlow vehicles.
    """
    selfish_vehicle_routes = computeSelfishVehicleRoutes(selfish_vehicles, landscape, AVERAGE_ROAD_SPEED_MPS)
    autoflow_vehicle_routes = computeAutoflowVehicleRoutes(autoflow_vehicles, landscape, AVERAGE_ROAD_SPEED_MPS)
    return (selfish_vehicle_routes, autoflow_vehicle_routes)

def computeSelfishVehicleRoutes(selfish_vehicles: list[Vehicle], landscape: Landscape, AVERAGE_ROAD_SPEED_MPS: float) -> list[list[tuple[float, float]]]:
    """
    Selfish routing algorithm of Google Maps.
    Vehicles are not knowledgeable of future traffic and therefore only aware of congestion AFTER they occur.

    Each node is a tuple that stores (fcost, hcost, gcost, tiebreaker, road, position).
    - fcost: sum of gcost and hcost, node with lowest fcost will be evaluated first
    - hcost: optimistic approximate time required to reach destination using AVERAGE_ROAD_SPEED
    - gcost: cost so far i.e. time taken so far, represents the ABSOLUTE time
    - tiebreaker: an unique integer used as a tiebreaker when all costs are equal

    Every node pushed into the Open list will be the start of a road (or the starting position of the vehicle).
    The Closed list contains all visited nodes (including end points of a road as well as the starting position).
    """

    routes: list[list[tuple[float, float]]] = []

    for vehicle in selfish_vehicles:

        tiebreaker = 0 # tiebreaker value for when all costs are equal

        # Hashmap that maps each node to their fcost
        node_fcost: dict[tuple[int, int], float] = defaultdict(lambda: float("inf"))

        # Hashmap that stores the previous node's roadID and normalised position of each node
        previous_node: dict[tuple[int, float], tuple[int, int]] = {}        
        # previous_node[(roadID, normalised position)] => (roadID, normalised position)
        # NOTE: normalised position is used to handle roads where startPosReal and endPosReal are equal
        
        # Calculate real destination position
        destination_position = getRealPositionOnRoad(vehicle.destinationRoad, vehicle.destinationPosition)

        # Nodes are the starting points of each road, can also be the starting point of the vehicle
        open_nodes: list[float, float, float, Road, float] = [] # Open is a priority queue
        closed_nodes: set[tuple(Road, float)] = set() # Closed can just be a set

        # Calculate the cost variables of the starting position
        gcost = 0
        hcost = euclideanDistance(
            getRealPositionOnRoad(vehicle.road, vehicle.position), 
            destination_position
        ) / AVERAGE_ROAD_SPEED_MPS
        fcost = gcost + hcost

        # Add starting position of the vehicle to open_nodes
        start_node = (fcost, hcost, gcost, tiebreaker, vehicle.road, vehicle.position)
        tiebreaker += 1
        heappush(open_nodes, start_node) 

        while True: # loop until target point has been reached

            if len(open_nodes) == 0:
                raise Exception("Path does not exist")

            # Explore the node with the lowest fcost (hcost is tiebreaker)
            fcost, hcost, gcost, tb, road, position = heappop(open_nodes)
            real_position = getRealPositionOnRoad(road, position)

            # Add current to closed_nodes
            closed_nodes.add((road, position))

            # If destination is same as current position (by chance) then skip this vehicle
            if road == vehicle.destinationRoad and position == vehicle.destinationPosition:
                break

            # If destination is on the same road in front of the current position then calculate single instruction
            if road == vehicle.destinationRoad and position < vehicle.destinationPosition:
                previous_node[(vehicle.destinationRoad.roadID, vehicle.destinationPosition)] = (road.roadID, position)
                break

            if (road, 1) in closed_nodes: # if current road is the starting road, skip
                continue

            # Otherwise, create instruction to move to the end of the road as there is no other choice
            roadEndPosition: tuple[float, float] = road.endPosReal

            # Store references to road intersection for easy reference
            road_start_intersection: Intersection = landscape.intersections[road.start]
            road_end_intersection: Intersection = landscape.intersections[road.end]

            # Initiate time cost of reaching road end node (ignoring traffic lights)
            time_taken = euclideanDistance(
                real_position,
                roadEndPosition
            ) / road.speedLimit_MPS

            # Compute waiting time until the next green light
            if len(road_end_intersection.neighbours) >= 3:
                current_modulus_time = gcost % (len(road_end_intersection.neighbours) * road_end_intersection.trafficLightDuration)
                if (
                    (road_end_intersection.trafficLightLookup[road_start_intersection] + 1) * road_end_intersection.trafficLightDuration 
                    > current_modulus_time
                ):
                    waiting_time = (
                        road_end_intersection.trafficLightLookup[road_start_intersection] * road_end_intersection.trafficLightDuration 
                        - current_modulus_time
                    )
                    if waiting_time > 0: # Case 1: current time is earlier in the cycle
                        pass
                    else: # Case 2: current time is within the green light duration, allow vehicle through
                        waiting_time = 0
                else: # Case 3: current time is later in the cycle
                    waiting_time = (
                        len(road_end_intersection.neighbours) * road_end_intersection.trafficLightDuration
                        - current_modulus_time 
                        + road_end_intersection.trafficLightLookup[road_start_intersection] * road_end_intersection.trafficLightDuration
                    )
                time_taken += waiting_time # update time taken to reflect traffic light waiting time

            # Set previous node of road end node to road start node
            previous_node[(road.roadID, 1)] = (road.roadID, position)

            # Add road end to closed nodes
            closed_nodes.add((road, 1))

            # Update variables
            position = 1
            real_position = roadEndPosition
            gcost += time_taken
            hcost = euclideanDistance(
                real_position, 
                destination_position
            ) / AVERAGE_ROAD_SPEED_MPS
            fcost = gcost + hcost

            # Examine neighbours
            for neighbour_intersection in road_end_intersection.neighbours:

                # No U turns allowed
                if neighbour_intersection == road_start_intersection:
                    continue

                # Store reference to neighbour road for easy reference
                neighbour_road = landscape.roadmap[road_end_intersection.coordinates()][neighbour_intersection.coordinates()]
                
                # If neighbour is in closed, skip
                if (neighbour_road, 0) in closed_nodes:
                    continue
                
                # Time cost of reaching neighbour node is the traversal time of virtual pathway
                time_taken = road_end_intersection.intersectionPathways[road_start_intersection][neighbour_intersection].traversalTime     
                # NOTE: traffic light waiting time is already accounted for by the gcost of reaching road end node

                # Compute all cost values
                neighbour_gcost = gcost + time_taken
                neighbour_hcost = euclideanDistance(
                    neighbour_road.startPosReal, 
                    destination_position
                ) / AVERAGE_ROAD_SPEED_MPS
                neighbour_fcost = neighbour_gcost + neighbour_hcost

                neighbour_node = (neighbour_fcost, neighbour_hcost, neighbour_gcost, tiebreaker, neighbour_road, 0)
                tiebreaker += 1

                # Push neighbour node into open list if fcost is smaller than the existing cost
                if neighbour_fcost < node_fcost[(neighbour_road, 0)]:
                    node_fcost[(neighbour_road, 0)] = neighbour_fcost
                    previous_node[(neighbour_road.roadID, 0)] = (road.roadID, 1)
                    heappush(open_nodes, neighbour_node) # it does not matter whether neighbour is already in open list

        # Initiate a list that stores the sequence of (next position, relative time taken) for the vehicle
        route = [] 

        # Initiate traceback variables
        current_roadID, current_position = vehicle.destinationRoad.roadID, vehicle.destinationPosition

        # Create route using previous_node hashmap
        while (current_roadID, current_position) in previous_node:

            # Unpack previous node information
            previous_roadID, previous_position = previous_node[(current_roadID, current_position)]
            
            # Append new instruction
            route.append((getRealPositionOnRoad(landscape.roads[current_roadID], current_position), current_roadID))

            # Update traceback variables
            current_roadID, current_position = previous_roadID, previous_position

        # Reverse instructions to obtain chronological order
        route.reverse()
        # print()
        # print(route)

        # Store computed route in routes list            
        routes.append(route)

    # for route in routes:
    #     print(routes)
    return routes

def MLSortVehicles(autoflow_vehicles):
    listVer = [
        [i.passengerCount, i.emissionRate, euclideanDistance(
                 getRealPositionOnRoad(i.road, i.position),
                 getRealPositionOnRoad(i.destinationRoad, i.destinationPosition)
             )]
          for i in autoflow_vehicles]
    
    indices = pred.predict(listVer)

    result = [0] * len(indices)

    for i in range(len(indices)):
        result[indices[i]] = autoflow_vehicles[i]
    
    return result

def sortVehicles(autoflow_vehicles: list[Vehicle]):
    """
    Sorts vehicles in-place baseed on a trainable priority function.
    """
        
    # result = MachineLearning.predict([
    #     [
    #         autoflow_vehicles[i].passengerCount, 
    #         autoflow_vehicles[i].emissionRate, 
    #         euclideanDistance(
    #             getRealPositionOnRoad(autoflow_vehicles[i].road, autoflow_vehicles[i].position),
    #             getRealPositionOnRoad(autoflow_vehicles[i].destinationRoad, autoflow_vehicles[i].destinationPosition)
    #         )
    #     ] for i in range(len(autoflow_vehicles))
    # ])
        
    # result = sorted(
    #     autoflow_vehicles,
    #     key = lambda vehicle: (            
    #         emissionRateWeighting * vehicle.emissionRate / Vehicle.MAX_EMISSION_RATE + 
    #         passengerCountWeighting * vehicle.passengerCount / Vehicle.MAX_PASSENGER_COUNT +
    #         distanceHeuristicWeighting * euclideanDistance(
    #             getRealPositionOnRoad(vehicle.road, vehicle.position),
    #             getRealPositionOnRoad(vehicle.destinationRoad, vehicle.destinationPosition)
    #         ) / (CELL_SIZE_METRES * 20 * 20)
    #     )
    # )

    autoflow_vehicles.sort(
        key = lambda vehicle: (      
            euclideanDistance(
                getRealPositionOnRoad(vehicle.road, vehicle.position),
                getRealPositionOnRoad(vehicle.destinationRoad, vehicle.destinationPosition)
            ) * vehicle.passengerCount,
            vehicle.emissionRate * -1
        ),
        reverse=True
    )

    return MLSortVehicles(autoflow_vehicles)

def computeAutoflowVehicleRoutes(autoflow_vehicles: list[Vehicle], landscape: Landscape, AVERAGE_ROAD_SPEED_MPS: float) -> list[list[tuple[float, float]]]:
    """
    AutoFlow vehicles perform cooperative A* with awareness of other AutoFlow vehicles.
    Vehicle priorities are determined by pre-trained gradient boosted regression trees.

    A space-time reservation table is used to keeps track of the number of vehicles on each road
    at any timestamp (in seconds). This greatly enhances the accuracy of cost functions when
    evaluating which path to take, as more congested roads would take longer to traverse.    

    Each node is a tuple that stores (fcost, hcost, gcost, tiebreaker, road, position).
    - fcost: sum of gcost and hcost, node with lowest fcost will be evaluated first
    - hcost: optimistic approximate time required to reach destination using AVERAGE_ROAD_SPEED
    - gcost: cost so far i.e. time taken so far, represents the ABSOLUTE time
    - tiebreaker: an unique integer used as a tiebreaker when all costs are equal

    Every node pushed into the Open list will be the start of a road (or the starting position of the vehicle).
    The Closed list contains all visited nodes (including end points of a road as well as the starting position).
    """

    routes: list[list[tuple[float, float]]] = []

    # Sort the list of vehicles
    sortVehicles(autoflow_vehicles)

    #delayFactor = len(landscape.roads) // max(landscape.xSize, landscape.ySize)
    # delayFactor = 1.5 # exponential time
    congestionCost = 1
    # print("DF:", delayFactor, "CC:", congestionCost)

    # Set up space-time reservation table 
    reservation_table: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    # reservation_table[roadID][timestamp in seconds] => number of vehicles on road at timestamp

    for vehicle in autoflow_vehicles:

        tiebreaker = 0 # tiebreaker value for when all costs are equal

        # Hashmap that maps each node to their fcost
        node_fcost: dict[tuple[int, int], float] = defaultdict(lambda: float("inf"))

        # Hashmap that stores the previous node, road index in landscape.roads and ABSOLUTE time cost of each node
        previous_node: dict[tuple[int, float], tuple[int, float, float]] = {}
        # previous_node[(roadID, normalised position)] => (roadID, normalised position, absolute time)
        # NOTE: normalised position is used to handle roads where startPosReal and endPosReal are equal
        # NOTE: ABSOLUTE time is needed to prevent time desync within reservation table
        
        # Calculate real destination position
        destination_position = getRealPositionOnRoad(vehicle.destinationRoad, vehicle.destinationPosition)

        # Nodes are the starting points of each road, can also be the starting point of the vehicle
        open_nodes: list[float, float, float, Road, float] = [] # Open is a priority queue
        closed_nodes: set[tuple(Road, float)] = set() # Closed can just be a set

        # Calculate the cost variables of the starting position
        gcost = 0
        hcost = euclideanDistance(
            getRealPositionOnRoad(vehicle.road, vehicle.position), 
            destination_position
        ) / AVERAGE_ROAD_SPEED_MPS
        fcost = gcost + hcost

        # Add starting position of the vehicle to open_nodes
        start_node = (fcost, hcost, gcost, tiebreaker, vehicle.road, vehicle.position)
        tiebreaker += 1
        heappush(open_nodes, start_node) 

        while True: # loop until target point has been reached

            if len(open_nodes) == 0:
                raise Exception("Path does not exist")

            # Explore the node with the lowest fcost (hcost is tiebreaker)
            fcost, hcost, gcost, tb, road, position = heappop(open_nodes)
            real_position = getRealPositionOnRoad(road, position)

            # Add current to closed_nodes
            closed_nodes.add((road, position))

            # If destination is same as current position (by chance) then skip this vehicle
            if road == vehicle.destinationRoad and position == vehicle.destinationPosition:
                break

            # If destination is on the same road in front of the current position then calculate single instruction
            if road == vehicle.destinationRoad and position < vehicle.destinationPosition:
                time_taken = euclideanDistance(
                    real_position,
                    destination_position
                ) / road.speedLimit_MPS # fastest time estimation from start of the road to the destination
                previous_node[(vehicle.destinationRoad.roadID, vehicle.destinationPosition)] = (
                    road.roadID, position, gcost + time_taken
                )
                break

            if (road, 1) in closed_nodes: # if current road is the starting road, skip
                continue

            # Otherwise, create instruction to move to the end of the road as there is no other choice
            roadEndPosition: tuple[float, float] = road.endPosReal

            # Store references to road intersection for easy reference
            road_start_intersection: Intersection = landscape.intersections[road.start]
            road_end_intersection: Intersection = landscape.intersections[road.end]

            # Initiate time cost of reaching road end node (ignoring traffic lights & any congestion)
            time_taken = euclideanDistance(
                real_position,
                roadEndPosition
            ) / road.speedLimit_MPS

            # Compute waiting time until the next green light
            if len(road_end_intersection.neighbours) >= 3:
                current_modulus_time = gcost % (len(road_end_intersection.neighbours) * road_end_intersection.trafficLightDuration)
                if (
                    (road_end_intersection.trafficLightLookup[road_start_intersection] + 1) * road_end_intersection.trafficLightDuration 
                    > current_modulus_time
                ):
                    waiting_time = (
                        road_end_intersection.trafficLightLookup[road_start_intersection] * road_end_intersection.trafficLightDuration 
                        - current_modulus_time
                    )
                    if waiting_time > 0: # Case 1: current time is earlier in the cycle
                        pass
                    else: # Case 2: current time is within the green light duration, allow vehicle through
                        waiting_time = 0
                else: # Case 3: current time is later in the cycle
                    waiting_time = (
                        len(road_end_intersection.neighbours) * road_end_intersection.trafficLightDuration
                        - current_modulus_time 
                        + road_end_intersection.trafficLightLookup[road_start_intersection] * road_end_intersection.trafficLightDuration
                    )
                time_taken += waiting_time # update time taken to reflect traffic light waiting time

                # Compute cost of reaching road end node (taking congestion into account)
                time_taken += (
                    reservation_table[road.roadID][int(gcost)]
                    // road_end_intersection.trafficPassthroughRate[road_start_intersection]
                    * road_end_intersection.trafficLightDuration * len(road_end_intersection.neighbours)
                ) # update time taken to reflect the number of traffic light cycles waited
                # print(reservation_table[road.roadID][int(gcost)])
                # print(road_end_intersection.trafficPassthroughRate[road_start_intersection])
                # print(road_end_intersection.trafficLightDuration)
                # print(road.speedLimit_MPS)
                # print()
                # print((
                #     reservation_table[road.roadID][int(gcost)]
                #     // road_end_intersection.trafficPassthroughRate[road_start_intersection]
                #     * road_end_intersection.trafficLightDuration
                # ))

            # Set previous node of road end node to road start node
            previous_node[(road.roadID, 1)] = (
                road.roadID, position, gcost + time_taken
            )

            # Add road end to closed nodes
            closed_nodes.add((road, 1))

            # Update variables
            position = 1
            real_position = roadEndPosition
            gcost += time_taken
            hcost = euclideanDistance(
                real_position, 
                destination_position
            ) / AVERAGE_ROAD_SPEED_MPS
            fcost = gcost + hcost

            # Examine neighbours
            for neighbour_intersection in road_end_intersection.neighbours:

                # No U turns allowed
                if neighbour_intersection == road_start_intersection:
                    continue

                # Store reference to neighbour road for easy reference
                neighbour_road = landscape.roadmap[road_end_intersection.coordinates()][neighbour_intersection.coordinates()]
                
                # If neighbour is in closed, skip
                if (neighbour_road, 0) in closed_nodes:
                    continue
                
                # Time cost of reaching neighbour node is the traversal time of virtual pathway
                time_taken = road_end_intersection.intersectionPathways[road_start_intersection][neighbour_intersection].traversalTime     
                # NOTE: traffic light waiting time is already accounted for by the gcost of reaching road end node

                # Compute all cost values
                neighbour_gcost = gcost + time_taken
                neighbour_hcost = euclideanDistance(
                    neighbour_road.startPosReal, 
                    destination_position
                ) / AVERAGE_ROAD_SPEED_MPS
                neighbour_fcost = neighbour_gcost + neighbour_hcost

                neighbour_node = (neighbour_fcost, neighbour_hcost, neighbour_gcost, tiebreaker, neighbour_road, 0)
                tiebreaker += 1

                # Push neighbour node into open list if fcost is smaller than the existing cost
                if neighbour_fcost < node_fcost[(neighbour_road, 0)]:
                    node_fcost[(neighbour_road, 0)] = neighbour_fcost
                    previous_node[(neighbour_road.roadID, 0)] = (
                        road.roadID, 1, -1 # skipped to avoid double marking in reservation table
                    )
                    heappush(open_nodes, neighbour_node) # it does not matter whether neighbour is already in open list

        # Initiate a list that stores the sequence of (next position, relative time taken) for the vehicle
        route = [] 

        # Initiate traceback variables
        current_roadID, current_position = vehicle.destinationRoad.roadID, vehicle.destinationPosition
        previousTimestamp = -1

        # Create route using previous_node hashmap
        while (current_roadID, current_position) in previous_node:

            # Unpack previous node information
            previous_roadID, previous_position, timestamp = previous_node[(current_roadID, current_position)]
            
            # Append new instruction
            route.append((getRealPositionOnRoad(landscape.roads[current_roadID], current_position), current_roadID))

            # Update congestion status of used road during the usage time period
            if previousTimestamp == -1:
                previousTimestamp = timestamp
            elif timestamp != -1: # skip virtual pathways for reservation table marking
                for i in range(int(timestamp), int(previousTimestamp)):
                    reservation_table[previous_roadID][i] += congestionCost              
                previousTimestamp = timestamp # update previous timestamp

            # Update traceback variables
            current_roadID, current_position = previous_roadID, previous_position

        # Reverse instructions to obtain chronological order
        route.reverse()
        # print()
        # print(route)

        # Store computed route in routes list                
        routes.append(route)

    # for route in routes:
    #     print(route)
    
    return routes

def recalculateRoutes(vehicleMetadata):
    # Double check that each car is within the bounds of its road
    for vehicle in vehicleMetadata:
        x, y = vehicle
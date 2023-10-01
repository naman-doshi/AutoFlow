"""
The old version of Autoflow submitted in R1.
"""


#================ IMPORTS ================
from LandscapeComponents import *
from VehicleAgents import *

import heapq
#=========================================


class GridState:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0  # Cost from start node to this node
        self.h = 0  # Heuristic (estimated cost from this node to goal)
        self.f = 0  # Total cost (g + h)

    def __lt__(self, other):
        # This method is used to compare GridState objects in the priority queue
        # We want to prioritize nodes with a lower f value (lower total cost)
        return self.f < other.f

def astar_search(landscape, start, end):
    open_set = []  # Priority queue to store open states
    closed_set = set()  # Set to store closed states

    # Initialize the start state
    start_node = GridState(start[0], start[1])
    start_node.g = 0
    start_node.h = heuristic(start_node, end)
    start_node.f = start_node.g + start_node.h

    # Push the start state onto the open set
    heapq.heappush(open_set, start_node)

    while open_set:
        current_node = heapq.heappop(open_set)  # Get the node with the lowest f value

        if (current_node.x, current_node.y) == end:
            # Found the goal, reconstruct the path
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            path.reverse()
            return path

        closed_set.add((current_node.x, current_node.y))

        # Generate neighbors
        neighbors = landscape.get_neighbors((current_node.x, current_node.y))

        for neighbor in neighbors:
            neighbor_x, neighbor_y = neighbor
            neighbor_node = GridState(neighbor_x, neighbor_y, current_node)

            if (neighbor_x, neighbor_y) in closed_set:
                continue

            tentative_g_score = current_node.g + landscape.get_cost((current_node.x, current_node.y), neighbor)
            
            if neighbor_node not in open_set or tentative_g_score < neighbor_node.g:
                neighbor_node.g = tentative_g_score
                neighbor_node.h = heuristic(neighbor_node, end)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                neighbor_node.parent = current_node

                if neighbor_node not in open_set:
                    heapq.heappush(open_set, neighbor_node)

    # No path found
    return None

# Define a heuristic function (e.g., Manhattan distance)
def heuristic(node, goal):
    return abs(node.x - goal[0]) + abs(node.y - goal[1])

# Example usage:
landscape = Landscape(xSize=10, ySize=10)
cars = [[(0, 0), (9, 9)], [(0, 9), (9, 0)], [(5, 5), (5, 7)], [(5, 5), (5, 3)]]
for car in cars:
    path = astar_search(landscape, car[0], car[1])
    if path == None:
        raise Exception("No path found, please try again")
    else:
        print(path)
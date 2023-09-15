from classdefs import *
import random

style = 'New York'
num_vertices = 50
num_vehicles = 20
width = 10
height = 5
prioritiseEV = False

vertices = []
roads = {}
vehicles = []



# Construct graph according to city
if style == "New York":
    dist_x = random.randint(1, 5)
    dist_y = random.randint(1, 5)
    dist_x /= 10
    dist_y /= 10
    # Create horizontal roads
    num = 0
    for i in range(height):
        for j in range(width):
            vert = Vertex(num, dist_x*j, dist_y*i)
            vertices.append(vert)
            roads[num] = {}
            num += 1

    



# Create vehicles
for i in range(num_vehicles):
    start = random.randint(0, num_vertices - 1)
    end = random.randint(0, num_vertices - 1)
    while end == start:
        end = random.randint(0, num_vertices - 1)
    vehicle = Vehicle(vertices[start], vertices[end], random.randint(1, 3))
    vehicles.append(vehicle)

vehicles.sort(key = lambda x: x.emissions_per_hour, reverse = not prioritiseEV)
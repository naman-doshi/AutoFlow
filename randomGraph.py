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
            if j != 0:
                road = Road.connect(vert, vertices[num-1], dist_x, random.randint(20, 60), random.randint(1, 30))
                roads[num-1][num] = road
            if i != 0:
                road = Road.connect(vert, vertices[num-width], dist_y, random.randint(20, 60), random.randint(1, 30))
                roads[num-width][num] = road
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
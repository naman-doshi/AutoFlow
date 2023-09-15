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

# Create vertices
for i in range(num_vertices):
	roads[i] = {}
	vertices.append(Vertex(i))

# Create vehicles
for i in range(num_vehicles):
	start = random.randint(0, num_vertices - 1)
	end = random.randint(0, num_vertices - 1)
	while end == start:
		end = random.randint(0, num_vertices - 1)
	vehicle = Vehicle(vertices[start], vertices[end], random.randint(1, 3))
	vehicles.append(vehicle)

vehicles.sort(key = lambda x: x.emissions_per_hour, reverse = not prioritiseEV)

# Construct graph according to city
if style == "New York":

	# New York — Grid structure
	for i in range(num_vertices):
		numLanes = random.randint(1, 3)
		speedLimit = random.randint(20, 60)
		length = random.randint(100, 200)
		length /= 1000
		if i % width != width - 1:
			road = Road.connect(vertices[i], vertices[i + 1], length, speedLimit, numLanes)
			roads[i][i + 1] = road
		if i < (height - 1) * width:
			road = Road.connect(vertices[i], vertices[i + width], length, speedLimit, numLanes)
			roads[i][i + width] = road


	



	

	
	

	


    
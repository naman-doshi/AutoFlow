# Hello from Naman

from Components import *

landscape = Landscape(xSize=5, ySize=5)

# landscape.gridMatrix = [
#     [None, (1, 0), (1, 0), None, None],
#     [None, (1, 0), (1, 0), (3, 1), (3, 1)],
#     [None, None, None, (3, 1), (3, 1)],
#     [(0, 3), (0, 3), (2, 3), (2, 3), None],
#     [(0, 3), (0, 3), (2, 3), (2, 3), None]
# ]

# landscape.gridMatrix = [
#     [None, (1, 0), (1, 0), (3, 0), (3, 0)],
#     [None, (1, 0), (1, 0), (3, 0), (3, 0)],
#     [(0, 2), (0, 2), (2, 2), (2, 2), None],
#     [(0, 2), (0, 2), (2, 2), (2, 2), None],
#     [None, None, None, None, None]
# ]

# landscape.gridMatrix = [
#     [None, None, None, (3, 0), (3, 0)],
#     [(0, 1), (0, 1), None, (3, 0), (3, 0)],
#     [(0, 1), (0, 1), (2, 2), (2, 2), None],
#     [(0, 3), (0, 3), (2, 2), (2, 2), None],
#     [(0, 3), (0, 3), None, None, None]
# ]

#landscape.generate_landscape_matrix()

#landscape.generate_new_landscape(desiredFeatures=[(LandPlotDescriptor((1, 1), (1, 1), False), 20)])
landscape.generate_new_landscape(filler=LandPlotDescriptor((2, 2), (2, 2), False))

#print(landscape.availableArea)

for i in range(len(landscape.gridMatrix)):
    print(landscape.gridMatrix[i])

print()

for i in range(1, len(landscape.landscapeMatrix)-1):
    print(landscape.landscapeMatrix[i][1:-1])
print()

# for i in range(len(landscape.landscapeMatrix)):
#     print(landscape.landscapeMatrix[i])



# Testing

# testMatrix = [[0 for i in range(landscape.xSize+2)] for j in range(landscape.ySize+2)]
# for road in landscape.roads:
#     if road.start[1] == road.end[1]: # horizontal road
#         for x in range(road.start[0]+1, road.end[0]):
#             testMatrix[road.start[1]][x] += 1
#     else: # vertical road
#         for y in range(road.start[1]+1, road.end[1]):
#             testMatrix[y][road.start[0]] += 1
# for x, y in landscape.intersections:
#     testMatrix[y][x] += 1
# for i in range(1, len(testMatrix)-1):
#     print(testMatrix[i][1:-1])
from ClassDefinitions import *

# Let each tick of time be the passing of a row of 3 cars on the main road (Point A)

endingTimes = []
roads = [Road(170), Road(120), Road(120)]

# In 2 seconds, how many cars can pass a point?
numPass = int((30 / 3.6) * 2 / 4.5) # Average length of car is 4.5m

tickSize = 4.5 / 30 * 3.6
currentTime = 0


for i in range(30):
  possibilites = []
  for j in range(3):
    road = roads[j]
    distanceUntilNextCar = abs(road.length - road.numCars * 4.5)
    timeToNextCar = distanceUntilNextCar / 30 * 3.6
    timeReachedNext = currentTime + timeToNextCar
    cyclesToWait = road.numCars // numPass

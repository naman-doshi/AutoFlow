from ClassDefinitions import *
import random

roads = [Road(1, 170), Road(2, 120), Road(3, 170)]
# In 2 seconds, how many cars can pass a point?
numPass = int((30 / 3.6) * 2 / 4.5) # Average length of car is 4.5m

# Car Generation
cars = []
numberCars = 10
for i in range(numberCars):
  cars.append(Car(i*2, random.randint(0, 100)))

currentTime = 0

endingtimes_selfish = []
commutingtimes_selfish = []
emissions_selfish = 0

for car in cars:
  t = car.departureTime
  greenLight = (t % 6) // 2
  roads[greenLight].numCars = max(0, roads[greenLight].numCars - numPass)
  possibilities = []

  for j in range(0, 3):
    road = roads[j]

    distToEnd = road.length - road.numCars * 4.5
    timeToEnd = distToEnd / 30 * 3.6
    timeToNextGreen = (j * 2) - ((t + timeToEnd) % 6)
    if timeToNextGreen < 0:
      timeToNextGreen += 6

    cyclesToNextGreen = road.numCars // numPass
    totalTime = timeToEnd + t
    if cyclesToNextGreen >= 1:
      totalTime += timeToNextGreen
    cyclesToNextGreen -= 1

    totalTime += 6 * cyclesToNextGreen

    possibilities.append(totalTime)

  currentTime = min(possibilities)
  endingtimes_selfish.append(currentTime)

  roads[possibilities.index(currentTime)].numCars += 1
  commutingtimes_selfish.append(currentTime - t)

  emissions_selfish += roads[possibilities.index(currentTime)].length * car.emissions

endingtimes_autoflow = []
commutingtimes_autoflow = []
emissions_autoflow = 0

cars.sort(key=lambda x: x.emissions)
for car in cars:

  

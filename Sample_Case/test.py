from ClassDefinitions import *
import random

trafficLightPeriod = 1
carSpeed = 40
numberCars = 500

if trafficLightPeriod <= 0 or trafficLightPeriod % 1 != 0:
  raise Exception("Traffic light period must be positive integer")

if carSpeed <= 0 or carSpeed % 1 != 0:
  raise Exception("Car speed must be positive integer")

if numberCars <= 0 or numberCars % 1 != 0:
  raise Exception("Number of cars must be positive integer")

roads = [Road(1, 170), Road(2, 120), Road(3, 170)]

# Creating traffic to begin with
for road in roads:
  road.numCars = random.randint(0, 10)

# In x seconds, how many cars can pass a point?
numPass = int((carSpeed / 3.6) * trafficLightPeriod / 4.5) # Average length of car is 4.5m

# Car Generation
cars = []
for i in range(numberCars):
  cars.append(Car(i*2, random.randint(0, 5)))

# Declaring variables
endingtimes_selfish = []
commutingtimes_selfish = []
emissions_selfish = 0
maxCongestion_selfish = 0

# SELFISH NAVIGATION

for car in cars:
  t = car.departureTime

  # Finding the maximum congestion
  for road in roads:
    maxCongestion_selfish = max(maxCongestion_selfish, road.numCars)

  # If the road is green-lighted, we can remove {numPass} cars from it
  if t % trafficLightPeriod == 0:
    greenLight = (t % (trafficLightPeriod * 3)) // trafficLightPeriod
    roads[greenLight].numCars = max(0, roads[greenLight].numCars - numPass)

  possibilities = []

  # For each road, we calculate the time it takes to reach the end
  for j in range(0, 3):
    road = roads[j]
    
    # Time to reach the back of the queue, or the end of the road
    distToEnd = abs(road.length - road.numCars * 4.5)
    timeToEnd = distToEnd / carSpeed * 3.6

    # Time to the next green light
    timeToNextGreen = (j * trafficLightPeriod) - ((t + timeToEnd) % (trafficLightPeriod * 3))
    if timeToNextGreen < 0:
      timeToNextGreen += trafficLightPeriod * 3

    
    # Number of cycles to the next green light
    cyclesToNextGreen = road.numCars // numPass

    # Total time to reach the end
    totalTime = timeToEnd + t

    if cyclesToNextGreen >= 1:
      totalTime += timeToNextGreen
      cyclesToNextGreen -= 1

    totalTime += trafficLightPeriod * 3 * cyclesToNextGreen

    possibilities.append(totalTime)
    

  # We choose the road with the minimum time
  currentTime = min(possibilities)

  endingtimes_selfish.append(currentTime)

  # We add the car to the road
  roads[possibilities.index(currentTime)].numCars += 1
  commutingtimes_selfish.append(currentTime - t)

  # We add the emissions
  emissions_selfish += roads[possibilities.index(currentTime)].length * car.emissions * 3/2


# ———————— AUTOFLOW ——————————

endingtimes_autoflow = []
commutingtimes_autoflow = []
emissions_autoflow = 0
maxCongestion_autoflow = 0

cars.sort(key=lambda x: x.emissions)

# 3 cars can have the best possible outcome (Road B)
# 6 cars can have the 2nd best outcome (Road A and C)
# and so on

assignedRoads = {}

# Ordered by shortest to longest
roadsOrdered = list(sorted(roads, key=lambda x: x.length))

# Keeps track of cars assigned to each road
stack = [[], [], []]

for i in range(numberCars):
  # Sort each substack
  stack = [sorted(stack[0], key=lambda x: x.departureTime), sorted(stack[1], key=lambda x: x.departureTime), sorted(stack[2], key=lambda x: x.departureTime)]
  
  car = cars[i]
  
  # If it's in the first {numPass * 3} cars, we MUST assign it the fastest possible road
  # At this point, we assume no cars come in between them, so they are all cleared in the first traffic light
  if i < numPass * 3:
    if i < numPass:
      road = roads[1]
      stack[0].append(car)

    elif i < numPass * 2:
      road = roads[0]
      stack[1].append(car)

    else:
      road = roads[2]
      stack[2].append(car)

  else:
    found = False

    # First you check if it can be the latest car in any road — so it doesnt interfere with anything
    for j in range(3):
      curStack = stack[j]
      if car.departureTime > stack[j][-1].departureTime:
        road = roadsOrdered[j]
        stack[j].append(car)
        found = True
        break
    
    # Then check if it's early enough to avoid every later car
    if not found:
      for j in range(3):
        curRoad = roads[j]
        
        # Since we assumed the road will be empty
        timeToNextGreen = (j * trafficLightPeriod) - ((car.departureTime + road.length / carSpeed * 3.6) % 6)
        if timeToNextGreen < 0:
          timeToNextGreen += trafficLightPeriod * 3

        # Time to finish navigating
        timeToNavigate = timeToNextGreen + road.length / carSpeed * 3.6

        # If it's already reached its destination before the next car reaches the traffic light,
        # it is OK to assign it to this road
        if timeToNavigate + car.departureTime < stack[j][0].departureTime + road.length / carSpeed * 3.6:
          road = roads[j]
          stack[j].append(car)
          found = True
          break

    # Last resort: displace the cars with the least emissions
    if not found:
      impacts = []
      for j in range(3):
        curStack = stack[j]
        tempEmissions = 0
        count = 0

        # Batches represents the batch that will be cleared in one traffic light
        # If the batch changes with the addition of a car, the changed batch car will be delayed
        batches = {}
        newBatches = {}

        for i in range(len(curStack)):
          # Original batch
          batches[curStack[::-1][i]] = i // numPass
          # New batch after adding car before it
          newBatches[curStack[::-1][i]] = (i + int(curStack[::-1][i].departureTime > car.departureTime)) // numPass

        for car2 in curStack:
          # Check if it's been adversely affected
          if newBatches[car2] != batches[car2]:
            tempEmissions += car2.emissions * roadsOrdered[j].length
            count += 1

        impacts.append(tempEmissions)
      
      # Choose route with least emission impact
      leastImpact = min(impacts)
      road = roadsOrdered[impacts.index(leastImpact)]
      stack[impacts.index(leastImpact)].append(car)
      found = True

    if not found:
      raise Exception(f"Car {i} could not be assigned to road")

  assignedRoads[car] = (car.departureTime, road)
  # print(car.emissions, car.departureTime, road.name)

# Sort cars by departure time to simulate sequence
sortedRoads = sorted(assignedRoads.items(), key=lambda kv:(kv[1], kv[0]))
sortedRoads = sortedRoads[::-1]

# Exact same as selfish calculations, but we don't need to determine which road
for car, road in sortedRoads:
  road = road[1]
  t = car.departureTime

  for roadx in roads:
    maxCongestion_autoflow = max(maxCongestion_autoflow, roadx.numCars)

  # If the road is green-lighted, we can remove {numPass} cars from it
  if t % trafficLightPeriod == 0:
    greenLight = (t % (trafficLightPeriod * 3)) // trafficLightPeriod
    roads[greenLight].numCars = max(0, roads[greenLight].numCars - numPass)

  distToEnd = abs(road.length - road.numCars * 4.5)
  timeToEnd = distToEnd / carSpeed * 3.6
  # print(timeToEnd)

  road.numCars += 1

  endingtimes_autoflow.append(totalTime)
  commutingtimes_autoflow.append(timeToEnd)
  emissions_autoflow += road.length * car.emissions

commutingtimes_autoflow.sort()
endingtimes_autoflow.sort()

print("Selfish Navigation:")
print("Median Commuting Time:", commutingtimes_selfish[len(commutingtimes_selfish) // 2])

# ERROR DETECTION
if commutingtimes_selfish[len(commutingtimes_selfish) // 2] <= 0:
  raise Exception("Median selfish commuting time is negative, please check custom parameters")

print("Ending Time:", max(endingtimes_selfish))
print("Total Emissions:", emissions_selfish)
print("Max Congestion:", maxCongestion_selfish)

print()

print("Autoflow:")
print("Median Commuting Time:", commutingtimes_autoflow[len(commutingtimes_autoflow) // 2])

# ERROR DETECTION
if commutingtimes_autoflow[len(commutingtimes_autoflow) // 2] <= 0:
  raise Exception("Median AutoFlow commuting time is negative, please check custom parameters")

print("Ending Time:", max(endingtimes_autoflow))
print("Total Emissions:", emissions_autoflow)
print("Max Congestion:", maxCongestion_autoflow)


  

  

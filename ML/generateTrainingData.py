import random

with open('ML/train.csv', 'a') as f:
  cars = []
  for i in range(1000):
    cars.append([random.randint(1, 6), random.randint(0, 900), random.randint(0, 1000)])
  cars.sort(key=lambda x: x[0]*x[2]+x[1], reverse=True)
  for i in range(len(cars)):
    car = cars[i]
    f.write(f'{car[0]},{car[1]},{car[2]},{i}\n')
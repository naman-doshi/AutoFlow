## Custon, barebones class definitions

class Road:
  def __init__(self, name, length):
    self.name = name
    self.length = length
    self.numCars = 0
  
  def is_on(self, time):
    return time % 6 < self.name * 2 and time % 6 >= self.name * 2 - 2

class Car:
  def __init__(self, departureTime, emissions):
    self.departureTime = departureTime
    self.emissions = emissions
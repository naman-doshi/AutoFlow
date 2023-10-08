"""
This script contains all of the vehicle agent object definitions required for the virtual simulation.

Vehicles are either conventional (run on fossil fuel) or electric (EVs) and contain the following fields:
- emissionRate: carbon emission in g/km, visit https://www.ntc.gov.au/light-vehicle-emissions-intensity-australia
- routingSystem: the routing system used by the vehicle

For future development, vehicle classes can be further divided to include extra properties,
e.g. different car model sizes, number of passengers, etc.
"""


# ================ IMPORTS ================
from LandscapeComponents import Road

from abc import *
from random import randint

# =========================================


class Vehicle(ABC):

    """
    Virtual representation of a vehicle on the map.
    """

    routingSystems = {0: "Selfish", 1: "Autoflow"}  # expandable

    @abstractmethod
    def __init__(self) -> None:
        self.emissionRate = 0

    def setRoutingSystem(self, systemID: int):
        self.routingSystem = Vehicle.routingSystems[systemID]

    def setLocation(self, road: Road, position: float):
        self.road = road  # the road the vehicle is currently on
        self.position = (
            position  # float between 0 and 1 indicating linear position along a road
        )
        road.vehicleStack.append(self)

    def setDestination(self, road: Road, position: float):
        self.destinationRoad = road
        self.destinationPosition = position

    def __deepcopy__(self, memo):
        agentCopy: Vehicle = self.__class__()
        agentCopy.setLocation(self.road, self.position)
        agentCopy.setDestination(self.destinationRoad, self.destinationPosition)
        agentCopy.routingSystem = self.routingSystem
        return agentCopy


class ConventionalVehicle(Vehicle):

    """
    Conventional vehicles run on fossil fuel, therefore their emission rate is positive.
    The vehicle's carbon emission per km is represented by its emissionRate field.

    Emission rate ranges from 100g/km to 250g/km for conventional vehicles.
    See https://www.ntc.gov.au/light-vehicle-emissions-intensity-australia for emission rate standards.
    """

    def __init__(
        self, emissionRate: float = randint(100, 250), passengerCount = randint(1, 6), useAutoFlow: bool = False
    ) -> None:
        self.emissionRate = emissionRate
        self.passengerCount = passengerCount
        self.setRoutingSystem(int(useAutoFlow))


class ElectricVehicle(Vehicle):

    """
    Electric vehicles run on electricity, therefore their emission rate is zero.
    """

    def __init__(
            self, passengerCount = randint(1, 6), useAutoFlow: bool = False
    ) -> None:
        self.emissionRate = 0
        self.passengerCount = passengerCount
        self.setRoutingSystem(int(useAutoFlow))

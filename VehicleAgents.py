from abc import *

class Vehicle(ABC):

    """
    Virtual representation of a vehicle on the map.
    """

    routingSystems = {0: "Isolated", 1: "Autoflow"} # expandable

    @abstractmethod
    def __init__(self) -> None:
        pass

    def setRoutingSystem(self, systemID: int):
        self.routingSystem = Vehicle.routingSystems[systemID]


class ConventionalVehicle(Vehicle):

    """
    Conventional vehicles run on fossil fuel, therefore their emission rate is positive.
    The vehicle's carbon emission per km is represented by its emissionRate field.
    """

    def __init__(self, emissionRate: float, useAutoFlow: bool = False) -> None:
        self.emissionRate = emissionRate
        self.setRoutingSystem(int(useAutoFlow))


class ElectricVehicle(Vehicle):

    """
    Electric vehicles run on electricity, therefore their emission rate is zero.
    """

    def __init__(self, useAutoFlow: bool = False) -> None:
        self.emissionRate = 0
        self.setRoutingSystem(int(useAutoFlow))
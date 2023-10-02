import asyncio
import dataclasses
from websockets.exceptions import ConnectionClosedOK
from websockets.server import WebSocketServerProtocol, serve
import json

from AutoFlowBridgeCompat import outputToBridge
from LandscapeComponents import Landscape
from VehicleAgents import Vehicle

PORT = 8001


@dataclasses.dataclass
class VehicleInitMessage:
    id: int
    position: tuple[float, float]
    rotation: float
    emissionRate: float

    def __dict__(self):
        return {
            "id": self.id,
            "position": self.position,
            "rotation": self.rotation,
            "emissionRate": self.emissionRate,
            "type": "VehicleInitMessage",
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return VehicleInitMessage(**d)


@dataclasses.dataclass
class Vector3Message:
    x: float
    y: float
    z: float

    def __dict__(self):
        return {"x": self.x, "y": self.y, "z": self.z}

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return Vector3Message(**d)


@dataclasses.dataclass
class Vector2Message:
    x: float
    y: float

    def __dict__(self):
        return {"x": self.x, "y": self.y}

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return Vector2Message(**d)


@dataclasses.dataclass
class RoadInitMessage:
    id: int
    speedLimit: float
    startPos: Vector2Message
    endPos: Vector2Message

    def __dict__(self):
        return {
            "id": self.id,
            "speedLimit": self.speedLimit,
            "startPos": self.startPos.__dict__(),
            "endPos": self.endPos.__dict__(),
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return RoadInitMessage(**d)


@dataclasses.dataclass
class InitMessage:
    tiles: list[str]
    rowWidth: int
    vehicles: list[VehicleInitMessage]
    roads: list[RoadInitMessage]

    def __dict__(self):
        return {
            "tiles": self.tiles,
            "rowWidth": self.rowWidth,
            "vehicles": [v.__dict__() for v in self.vehicles],
            "roads": [r.__dict__() for r in self.roads],
            "type": "InitMessage",
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return InitMessage(**d)


@dataclasses.dataclass
class VehicleUpdateMessage:
    id: int
    route: list[Vector3Message]

    def __dict__(self):
        return {
            "id": self.id,
            "route": [r.__dict__() for r in self.route],
            "type": "VehicleUpdateMessage",
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return VehicleInitMessage(**d)


@dataclasses.dataclass
class UpdateMessage:
    updates: list[VehicleUpdateMessage]

    def __dict__(self):
        return {
            "updates": [u.__dict__() for u in self.updates],
            "type": "UpdateMessage",
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return VehicleInitMessage(**d)


class JSONUtils:
    @staticmethod
    def deserialize(text: str):
        d: dict = json.loads(text)
        typ = d.pop("type")

        match typ:
            case "InitMessage":
                return InitMessage.deserialize(d)
            case "VehicleMessage":
                return VehicleInitMessage.deserialize(d)
            case _:
                raise ValueError("Invalid type from JSON")


USE_AUTOFLOW = True


async def handler(websocket: WebSocketServerProtocol):
    print("Session opened")
    inp: tuple[
        dict[int, tuple[float, float]],
        Landscape,
        dict[int, list[tuple[float, float, float]]],
        list[Vehicle],
    ] = outputToBridge(USE_AUTOFLOW)

    # Initial scene
    vehicleInits = []
    for id, pos in inp[0].items():
        vehicleInits.append(VehicleInitMessage(id, pos, 0, inp[3][id].emissionRate))

    flatLandscapeMatrix = []
    for row in inp[1].landscapeMatrix:
        flatLandscapeMatrix.extend(row)

    roadMessages = []
    for road in inp[1].roads:
        roadMessages.append(
            RoadInitMessage(
                road.roadID,
                road.speedLimit_MPS,
                Vector2Message(road.startPosReal[0], road.startPosReal[1]),
                Vector2Message(road.endPosReal[0], road.endPosReal[1]),
            )
        )

    await websocket.send(
        InitMessage(
            flatLandscapeMatrix,
            len(inp[1].landscapeMatrix[0]),
            vehicleInits,
            roadMessages,
        ).serialize()
    )
    print("Finished terrain")
    await asyncio.sleep(0.5)

    # Updates
    updateMessages = []
    for id, route in inp[2].items():
        currentCar = VehicleUpdateMessage(id, [Vector3Message(*r) for r in route])
        updateMessages.append(currentCar)
    await websocket.send(UpdateMessage(updateMessages).serialize())

    print("Finished routing")


async def main():
    async with serve(handler, "localhost", PORT):
        await asyncio.Future()  # run forever


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")

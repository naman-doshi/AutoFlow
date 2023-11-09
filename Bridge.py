import asyncio
import dataclasses
from websockets.exceptions import ConnectionClosedOK
from websockets.server import WebSocketServerProtocol, serve
import json

from AutoFlowBridgeCompat import outputToBridge
from LandscapeComponents import Landscape
from VehicleAgents import Vehicle
import websockets
import AutoFlowBridgeCompat
import LandscapeComponents
from LandscapeComponents import Road
from AutoFlow import recalculateRoutes
from AutoFlowBridgeCompat import AVERAGE_ROAD_SPEED_MPS

PORT = 8001


@dataclasses.dataclass
class VehicleInitMessage:
    id: int
    initRoadId: int
    position: tuple[float, float]
    rotation: float
    emissionRate: float
    useAutoFlow: bool
    passengerCount: int

    def __dict__(self):
        return {
            "id": self.id,
            "initRoadId": self.initRoadId,
            "position": self.position,
            "rotation": self.rotation,
            "emissionRate": self.emissionRate,
            "useAutoFlow": self.useAutoFlow,
            "passengerCount": self.passengerCount,
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
class IntersectionMessage:
    id: Vector2Message
    enterRoadIDs: list[int]
    exitRoadIDs: list[int]
    pattern: list[int]
    greenDuration: float

    def __dict__(self):
        return {
            "id": self.id.__dict__(),
            "enterRoadIDs": self.enterRoadIDs,
            "exitRoadIDs": self.exitRoadIDs,
            "pattern": self.pattern,
            "greenDuration": self.greenDuration,
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return IntersectionMessage(**d)


@dataclasses.dataclass
class InitMessage:
    tiles: list[str]
    rowWidth: int
    vehicles: list[VehicleInitMessage]
    roads: list[RoadInitMessage]
    intersections: list[IntersectionMessage]

    def __dict__(self):
        return {
            "tiles": self.tiles,
            "rowWidth": self.rowWidth,
            "vehicles": [v.__dict__() for v in self.vehicles],
            "roads": [r.__dict__() for r in self.roads],
            "intersections": [i.__dict__() for i in self.intersections],
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


async def handler(websocket: WebSocketServerProtocol):
    # User input
    print("Session opened")
    USE_AUTOFLOW = False if input("Use AutoFlow (y/n)? ").startswith("n") else True
    print(USE_AUTOFLOW)

    inp: tuple[
        dict[int, tuple[float, float, Vehicle]],
        Landscape,
        dict[int, list[tuple[float, float, float]]],
        list[Vehicle],
    ] = outputToBridge(USE_AUTOFLOW)


    # Initial scene
    vehicleInits = []
    for id, posAndVeh in inp[0].items():
        vehicleInits.append(
            VehicleInitMessage(
                id,
                posAndVeh[2].road.roadID,
                (posAndVeh[0], posAndVeh[1]),
                0,
                inp[3][id].emissionRate,
                USE_AUTOFLOW,
                posAndVeh[2].passengerCount,
            )
        )

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

    intersections = [
        IntersectionMessage(Vector2Message(i[0][0], i[0][1]), i[1], i[2], i[3], i[4])
        for i in inp[1].unityCache
    ]

    await websocket.send(
        InitMessage(
            flatLandscapeMatrix,
            len(inp[1].landscapeMatrix[0]),
            vehicleInits,
            roadMessages,
            intersections,
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
    
    roadLookup : dict[tuple[int, int], Road] = {}
    for road in inp[1].roads:
        roadLookup[(int(road.startPosReal[0]), int(road.startPosReal[1]))] = road
        roadLookup[(int(road.endPosReal[0]), int(road.endPosReal[1]))] = road
        
    # print(roadLookup)
    if USE_AUTOFLOW:
        while True:
            try:
                message = await websocket.recv()
                # horrible security
                carPositions = eval(message)
                updateMessages = []

                newRoutes = recalculateRoutes(carPositions, inp[1], inp[3], AVERAGE_ROAD_SPEED_MPS)

                for k in newRoutes:
                    currentCar = VehicleUpdateMessage(id, [Vector3Message(*r) for r in k])
                    updateMessages.append(currentCar)

                await websocket.send(UpdateMessage(updateMessages).serialize())
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed, stopping reception.")
                break

            await asyncio.sleep(5)



async def main():
    async with serve(handler, "localhost", PORT):
        await asyncio.Future()  # run forever


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")

import asyncio
import dataclasses
import random
from websockets.exceptions import ConnectionClosedOK
from websockets.server import WebSocketServerProtocol, serve
import json

PORT = 8001


@dataclasses.dataclass
class VehicleInitMessage:
    id: int
    position: tuple[float, float]
    rotation: float

    def __dict__(self):
        return {
            "id": self.id,
            "position": self.position,
            "rotation": self.rotation,
            "type": "VehicleInitMessage",
        }

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return VehicleInitMessage(**d)


@dataclasses.dataclass
class InitMessage:
    tiles: list[str]
    rowWidth: int
    vehicles: list[VehicleInitMessage]

    def __dict__(self):
        return {
            "tiles": self.tiles,
            "rowWidth": self.rowWidth,
            "vehicles": [v.__dict__() for v in self.vehicles],
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
    position: tuple[float, float]
    relativeTime: float

    def __dict__(self):
        return {
            "id": self.id,
            "position": self.position,
            "relativeTime": self.relativeTime,
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
    print("Session opened")
    await websocket.send(
        InitMessage(
            ["HR", "HR", "HR", "HR"], 2, [VehicleInitMessage(0, (0, 0), 0)]
        ).serialize()
    )

    while True:
        try:
            await websocket.send(
                UpdateMessage(
                    [
                        VehicleUpdateMessage(
                            0, (random.randrange(-20, 20), random.randrange(-20, 20)), 2
                        )
                    ]
                ).serialize()
            )
            await asyncio.sleep(1)
        except ConnectionClosedOK:
            print("Session closed")
            break


async def main():
    async with serve(handler, "localhost", PORT):
        await asyncio.Future()  # run forever


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")

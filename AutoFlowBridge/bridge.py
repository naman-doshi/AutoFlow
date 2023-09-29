import asyncio
import dataclasses
from websockets.server import WebSocketServerProtocol, serve
import json

PORT = 8001


@dataclasses.dataclass
class InitMessage:
    matrix: list[list[str]]

    def __dict__(self):
        return {"message": self.matrix, "type": "InitMessage"}

    def serialize(self):
        return json.dumps(self.__dict__())

    @staticmethod
    def deserialize(d):
        return InitMessage(**d)


class JSONUtils:
    @staticmethod
    def deserialize(text: str):
        d: dict = json.loads(text)
        typ = d.pop("type")

        match typ:
            case "InitMessage":
                return InitMessage.deserialize(d)
            case _:
                raise ValueError("Invalid type from JSON")


async def handler(websocket: WebSocketServerProtocol):
    # Initialiize Unity Client
    await websocket.send(InitMessage([["HR", "HR"], ["HR", "HR"]]).serialize())
    while True:
        await asyncio.sleep(1)

    # while True:
    #     msg = await websocket.recv()
    #     initMessage = JSONUtils.des
    #     # Receive
    #     async for message in websocket:
    #         print(message)

    #     await asyncio.sleep(1)


async def main():
    async with serve(handler, "localhost", PORT):
        try:
            await asyncio.Future()  # run forever
        except asyncio.CancelledError:
            print("Terminated")


asyncio.run(main())

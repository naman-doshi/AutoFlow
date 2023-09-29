import asyncio

import websockets
from websockets.client import WebSocketClientProtocol


async def handler(websocket: WebSocketClientProtocol):
    async for message in websocket:
        print(message)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3.9

import asyncio
import ssl
import websockets
from status import *
from pathlib import Path


HOST = "0.0.0.0"
PORT = 6001
FULLCHAIN_PATH = Path('/etc/letsencrypt/live/miramontes.dev/fullchain.pem')
PRIVKEY_PATH = Path('/etc/letsencrypt/live/miramontes.dev/privkey.pem')


async def main(websocket, path):
    while True:
        request = await websocket.recv()
        print(request)
        await websocket.send("Hello, Friend")


def bootstrap():
    info("Starting server ...")
    loop = asyncio.get_event_loop()

    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(FULLCHAIN_PATH, keyfile=PRIVKEY_PATH)
    except PermissionError:
        fatal("Could not load {} or {}".format(FULLCHAIN_PATH, PRIVKEY_PATH))

    server_task = websockets.serve(main, HOST, PORT, ssl=ssl_context)

    loop.run_until_complete(server_task)
    success("Server ready");

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        success("Server shutdown")


if __name__ == '__main__':
    try:
        bootstrap()
    except FatalException:
        pass

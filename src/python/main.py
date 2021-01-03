#!/usr/bin/env python3.9
import asyncio
import json
import os
import ssl
import signal
import websockets
from dataclasses import dataclass
from status import *
from pathlib import Path
from handlers import request_handlers
from typing import Any


HOST = "0.0.0.0"
FULLCHAIN_PATH = Path('/drawing-game/secrets/fullchain.pem')
PRIVKEY_PATH = Path('/drawing-game/secrets/privkey.pem')


connected_sockets = set()


async def attempt_broadcast(websocket, message):
    try:
        await websocket.send(message)
        return websocket, True
    except:
        return websocket, False


@dataclass
class RequestContext:
    websocket: Any
    requester: str
    message: dict

    async def broadcast(self, message, *, group=None):
        if group is None:
            group = connected_sockets
        if not isinstance(message, str):
            message = json.dumps(message)

        results = await asyncio.gather(*(
            attempt_broadcast(sock, message)
            for sock in group if sock is not self.websocket
        ))

        successes = 0
        for websocket, result in results:
            if result:
                successes += 1
            else:
                group.discard(websocket)
        return successes

    async def send(self, message):
        if not isinstance(message, str):
            message = json.dumps(message)
        await self.websocket.send(message)



async def wrap_main(websocket, path):
    try:
        await main(websocket, path)
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        connected_sockets.discard(websocket)


async def main(websocket, path):
    connected_sockets.add(websocket)

    # Get "connect" request
    event = await websocket.recv()

    if not isinstance(event, str):
        error("Malformed client handshake: not string")
        return

    try:
        message = json.loads(event)
    except json.JSONDecodeError:
        error("Malformed client handshake: not JSON")
        return

    if message.get('type', None) != "connect":
        error("Malformed client handshake: no connect request")
        return

    token = message.get('token', None)
    if not token:
        error("Malformed client handshake: no connect token")
        return

    info("Received connection from", token)
    await websocket.send('{"type": "connected"}')

    # Receive requests
    while True:
        # Receive a request
        event = await websocket.recv()

        # Validate the request
        if isinstance(event, str):
            try:
                message = json.loads(event)
            except json.JSONDecodeError:
                error("Malformed JSON request")
                continue
        elif isinstance(event, bytes):
            error("Bytes frame type not implemented")
            continue
        else:
            error("Unknown frame type '{}' from websocket.recv()".format(type(frame)))
            continue

        if 'type' not in message:
            error("Malformed message: missing a type")
            continue

        # Call the appropriate handler
        if message['type'] in request_handlers:
            try:
                context = RequestContext(websocket, token, message)
                validate, handler = request_handlers[message['type']]
                validate(message)
                reply = await handler(context)
            except Exception as e:
                reply = "{}: {}".format(type(e).__name__, str(e))
                error(reply)
        else:
            reply = "Unrecognized message type '{}'".format(message['type'])
            error(reply)

        # If reply is None, turn it into success
        if reply is None:
            reply = {"type": "success"}

        # If reply is a string, turn it into an error
        if isinstance(reply, str):
            reply = {"type": "error", "data": reply}

        # Make sure request id is preserved
        request_id = message.get('id', None)
        if request_id:
            reply['id'] = request_id

        # Serialize and send the reply
        await websocket.send(json.dumps(reply))


def start_server():
    WS_UNSECURE = os.environ.get('WS_UNSECURE') == "true"
    PORT = int(os.environ.get('CONTAINER_PORT'))

    info("Starting server ...")
    loop = asyncio.get_event_loop()

    # Set up SIGTERM handler
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda: loop.stop())

    if WS_UNSECURE:
        # Start server with no SSL
        server_task = websockets.serve(wrap_main, HOST, PORT)
    else:
        # Load SSL certs
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(FULLCHAIN_PATH, keyfile=PRIVKEY_PATH)
        except PermissionError:
            fatal("Could not load {} or {}".format(FULLCHAIN_PATH, PRIVKEY_PATH))

        # Start server with SSL
        server_task = websockets.serve(wrap_main, HOST, PORT, ssl=ssl_context)

    loop.run_until_complete(server_task)
    success("Server ready")

    # Wait until a SIGTERM is received or CTRL+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print()

    success("Server shutdown")


if __name__ == '__main__':
    try:
        start_server()
    except FatalException as e:
        error(e, end="")

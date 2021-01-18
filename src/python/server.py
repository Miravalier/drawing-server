#!/usr/bin/env python3.9
import asyncio
import json
import os
import ssl
import signal
import websockets
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import app
import task
from handler import request_handlers, register
from messages import *


HOST = "0.0.0.0"
FULLCHAIN_PATH = Path('/server/secrets/fullchain.pem')
PRIVKEY_PATH = Path('/server/secrets/privkey.pem')


connected_sockets = set()
player_contexts = {}


@register("ping")
async def on_ping(ctx, message):
    """
    Used for debugging. Sends the received message back with a type of pong.
    """
    info("Received ping:", message, "from", ctx);
    message["type"] = "pong"
    return message


async def attempt_broadcast(websocket, message):
    try:
        await websocket.send(message)
        return websocket, True
    except:
        return websocket, False


class PlayerContext:
    def __init__(self, token):
        self.token = token
        self.websocket = None
        self.last_checkin = None
        self.path = None

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

    async def handle(self, message):
        # Call the appropriate handler
        if message['type'] in request_handlers:
            try:
                validate, handler = request_handlers[message['type']]
                validate(message)
                reply = await handler(self, message)
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
        await self.websocket.send(json.dumps(reply))

    async def handle_loop(self):
        # Receive requests
        while True:
            # Receive a request
            event = await self.websocket.recv()

            # Update last checkin
            self.last_checkin = datetime.now()

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

            # Handle the request
            await self.handle(message)


async def main(websocket, path):
    try:
        # Get initial request
        event = await websocket.recv()

        # Make sure request is a string
        if not isinstance(event, str):
            error("Malformed client handshake: not string")
            return

        # Make sure request is valid JSON
        try:
            message = json.loads(event)
        except json.JSONDecodeError:
            error("Malformed client handshake: not JSON")
            return

        # Make sure request is either connect or reconnect
        if message.get('type', None) not in ("connect", "reconnect"):
            error("Malformed client handshake: no connect request")
            return

        # Make sure request has a token
        token = message.get('token', None)
        if not token:
            error("Malformed client handshake: no connect token")
            return

        info("Received connection from", token)

        # Get old context or create new one
        ctx = player_contexts.get(token, None)
        if ctx is None:
            if message['type'] != "connect":
                error("Malformed client handshake: reconnect without session")
                return
            ctx = PlayerContext(token)
            player_contexts[token] = ctx

        # Disconnect old websocket
        if ctx.websocket:
            await ctx.websocket.close()
            ctx.websocket = None

        # Update context websocket, path, and last_checkin
        ctx.websocket = websocket
        ctx.last_checkin = datetime.now()
        ctx.path = path

        # Add websocket to connected sockets
        connected_sockets.add(websocket)

        # Handle initial message
        await ctx.handle(message)

        # Go into handle loop
        await ctx.handle_loop()
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        connected_sockets.discard(websocket)


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
        server_task = websockets.serve(main, HOST, PORT)
    else:
        # Load SSL certs
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(FULLCHAIN_PATH, keyfile=PRIVKEY_PATH)
        except PermissionError:
            fatal("Could not load {} or {}".format(FULLCHAIN_PATH, PRIVKEY_PATH))

        # Start server with SSL
        server_task = websockets.serve(main, HOST, PORT, ssl=ssl_context)

    loop.run_until_complete(server_task)
    loop.run_until_complete(task.init())
    loop.run_until_complete(app.init())

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

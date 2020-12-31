#!/usr/bin/env python3.9
import asyncio
import json
import ssl
import websockets
from status import *
from pathlib import Path
from handlers import request_handlers


HOST = "0.0.0.0"
PORT = 14501
FULLCHAIN_PATH = Path('/drawing-game/secrets/fullchain.pem')
PRIVKEY_PATH = Path('/drawing-game/secrets/privkey.pem')


connected_sockets = set()


async def wrap_main(websocket, path):
    try:
        await main(websocket, path)
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        connected_sockets.discard(websocket)


async def main(websocket, path):
    connected_sockets.add(websocket)
    while True:
        # Receive a request
        event = await websocket.recv()
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

        # Validate the request
        if 'type' not in message:
            error("Malformed message missing a type")
            continue

        # Call the appropriate handler
        if message['type'] in request_handlers:
            try:
                reply = request_handlers[message['type']](websocket, message)
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
        request_id = message.get('requestId', None)
        if request_id:
            reply['requestId'] = request_id

        # Serialize and send the reply
        await websocket.send(json.dumps(reply))


def start_server():
    info("Starting server ...")
    loop = asyncio.get_event_loop()

    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(FULLCHAIN_PATH, keyfile=PRIVKEY_PATH)
    except PermissionError:
        fatal("Could not load {} or {}".format(FULLCHAIN_PATH, PRIVKEY_PATH))

    server_task = websockets.serve(wrap_main, HOST, PORT, ssl=ssl_context)

    loop.run_until_complete(server_task)
    success("Server ready");

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

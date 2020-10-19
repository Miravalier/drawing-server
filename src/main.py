#!/usr/bin/env python3.9
import asyncio
import sys

from client import Client
from protocol import *


clients = {}


async def main():
    print(sys.version)
    await asyncio.start_server(connection_callback, "0.0.0.0", 1000)


async def connection_callback(reader, writer):
    # Read the type and id from the connection
    client_type = int.from_bytes(await reader.readexactly(1))
    client_id = int.from_bytes(await reader.readexactly(16), 'big')
    # Get the client object
    if client_id in clients:
        client = clients[client_id]
    else:
        client = Client(client_id)
        clients[client_id] = client
    # TX Connection
    if client_type == 0x01:
        if client.receiver is None:
            print("New receiver connection from {}.".format(client_id))
        else:
            client.receiver.close()
        client.receiver = ConnectionPair(reader, writer)


if __name__ == '__main__':
    asyncio.run(main())

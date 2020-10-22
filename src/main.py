#!/usr/bin/env python3.9
import asyncio
import sys
from asyncio import StreamReader, StreamWriter

from client import Client, ConnectionPair
from protocol import *
from game import Lobby


clients = {}


async def main():
    print(sys.version)
    print("Info: Server starting up.")
    server = await asyncio.start_server(connection_callback, "0.0.0.0", 1000)
    await server.serve_forever()
    print("Info: Server shut down.")


def repeat(coro):
    async def wrapper(*args, **kwargs):
        try:
            while True:
                await coro()
        except:
            pass
    return wrapper


@repeat
async def client_handler(client: Client):
    packet_type, stream = await client.receive()
    if packet_type == SET_LITTLE_ENDIAN:
        client.byteorder = 'little'
    elif packet_type == SET_BIG_ENDIAN:
        client.byteorder = 'big'
    elif packet_type == KEEPALIVE:
        pass
    elif packet_type == DISCONNECT:
        client.disconnect()
    elif packet_type == CREATE_LOBBY:
        pass
    elif packet_type == SET_NAME:
        client.name = stream.get_string()
        print("Client {} renamed to {}".format(client.id, client.name))


async def connection_callback(reader: StreamReader, writer: StreamWriter):
    # Read the type and id from the connection
    try:
        client_type = int.from_bytes(await reader.readexactly(1), 'big')
        client_id = int.from_bytes(await reader.readexactly(16), 'big')
    except EOFError:
        return

    # Get the client object if it exists
    if client_id in clients:
        client = clients[client_id]
    # Create the client object otherwise
    else:
        client = Client(client_id)
        asyncio.create_task(client_handler(client))
        clients[client_id] = client

    # Store the transmitter or receiver on the client object
    if client_type == CLIENT_TYPE_TRANSMITTER:
        if client.transmitter is None:
            print("Info: New transmitter connection from {}.".format(client_id))
        else:
            print("Info: Re-established transmitter connection from {}".format(client_id))
            client.transmitter.close()
        client.transmitter = ConnectionPair(reader, writer)
    elif client_type == CLIENT_TYPE_RECEIVER:
        if client.receiver is None:
            print("Info: New receiver connection from {}.".format(client_id))
        else:
            print("Info: Re-established receiver connection from {}".format(client_id))
            client.receiver.close()
        client.receiver = ConnectionPair(reader, writer)
    else:
        print("Error: Unknown client type", client_type)

    # If both transmitter and receiver have been stored, mark the client as ready
    if client.transmitter is not None and client.receiver is not None:
        print("Info: Client {} is ready.".format(client_id))
        client.ready.set()


if __name__ == '__main__':
    asyncio.run(main())

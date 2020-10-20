import asyncio
from asyncio import StreamReader, StreamWriter, Event
from bytestream import ByteStream
from dataclasses import dataclass, field


@dataclass
class ConnectionPair:
    reader: StreamReader = field(default=None)
    writer: StreamWriter = field(default=None)

    async def send(self, data: bytes):
        self.writer.write(data)
        await self.writer.drain()

    async def receive(self, count: int) -> bytes:
        await self.reader.readexactly(count)

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()


@dataclass
class Client:
    id: int
    byteorder: str = field(default='little')
    receiver: ConnectionPair = field(default=None)
    transmitter: ConnectionPair = field(default=None)
    ready: Event = field(default_factory=Event)
    connected: bool = field(default=True)
    _name: str = field(default=None)

    @property
    def name(self):
        if self._name is not None:
            return self._name
        return hex(self.id)[2:]

    @name.setter
    def name(self, value):
        self._name = value

    def disconnect(self):
        self.connected = False
        self.ready.set()

    async def reconnect_pairs(self):
        if self.connected:
            self.ready.clear()
            await asyncio.gather(
                self.receiver.close(),
                self.transmitter.close()
            )
            # The client will reach back out and re-connect these
            self.receiver = None
            self.transmitter = None

    async def send(self, packet_type: int, stream: ByteStream):
        # Build the packet
        data = (
            packet_type.to_bytes(2, self.byteorder)
            + len(stream).to_bytes(4, self.byteorder)
            + stream.to_bytes()
        )
        # Try to send it until it succeeds or the client closes
        while True:
            try:
                await self.ready.wait()
                if not self.connected:
                    return
                await self.transmitter.send(data)
                break
            except OSError:
                await self.reconnect_pairs()

    async def receive(self) -> tuple[int, ByteStream]:
        # Try to receive a packet until it succeeds or the client closes
        while True:
            try:
                await self.ready.wait()
                if not self.connected:
                    return DISCONNECT, ByteStream(byteorder=self.byteorder)
                packet_type = int.from_bytes(await self.receiver.receive(1), self.byteorder, signed=False)
                length = int.from_bytes(await self.receiver.receive(4), self.byteorder, signed=False)
                stream = ByteStream(await self.receiver.receive(length), byteorder=self.byteorder)
                return packet_type, stream
            except OSError:
                await self.reconnect_pairs()

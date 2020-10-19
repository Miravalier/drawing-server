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
    receiver: ConnectionPair = field(default=None)
    transmitter: ConnectionPair = field(default=None)

    async def send(self, packet_type: int, data: ByteStream):
        pass

    async def receive(self) -> tuple[int, ByteStream]:
        pass

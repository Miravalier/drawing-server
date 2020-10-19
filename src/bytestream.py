from typing import Union
import struct


class Bytestream:
    def __init__(self, data: Union[int, bytes, bytearray, None] = None, byteorder='little'):
        if data is None:
            self.data = bytearray()
        else:
            self.data = bytearray(data)
        self.byteorder = byteorder
        self.offset = 0
        self.count = len(self.data)

    @property
    def capacity(self):
        return len(self.data)

    def __len__(self):
        return self.count

    def seek_absolute(self, offset: int) -> int:
        self.offset = max(min(offset, self.count), 0)
        return self.offset

    def seek_relative(self, offset: int) -> int:
        self.offset = max(min(self.offset + offset, self.count), 0)
        return self.offset

    def seek_start(self) -> int:
        self.offset = 0
        return self.offset

    def seek_end(self) -> int:
        self.offset = self.count
        return self.offset

    def ensure_space(size: int):
        if self.offset + size <= self.capacity:
            return
        capacity = self.capacity
        while self.offset + size > capacity:
            capacity *= 2
        resized_data = bytearray(capacity)
        resized_data[:len(self.data)] = self.data
        self.data = resized_data

    def put_bytes(value: bytes):
        self.ensure_space(len(value))
        self.data[self.offset : self.offset + len(value)] = value
        self.offset += len(value)
        self.count = max(self.count, self.offset)

    def put_uint64(value: int):
        self.put_bytes(value.to_bytes(8, self.byteorder, signed=False))

    def put_uint32(value: int)
        self.put_bytes(value.to_bytes(4, self.byteorder, signed=False))

    def put_uint16(value: int)
        self.put_bytes(value.to_bytes(2, self.byteorder, signed=False))

    def put_byte(value: int)
        self.put_bytes(value.to_bytes(1, self.byteorder, signed=False))

    def put_int64(value: int):
        self.put_bytes(value.to_bytes(8, self.byteorder, signed=True))

    def put_int32(value: int)
        self.put_bytes(value.to_bytes(4, self.byteorder, signed=True))

    def put_int16(value: int)
        self.put_bytes(value.to_bytes(2, self.byteorder, signed=True))

    def put_signed_byte(value: int)
        self.put_bytes(value.to_bytes(1, self.byteorder, signed=True))

    def put_string(value: Union[str, bytes]):
        if isinstance(value, str):
            value = value.encode('utf-8')
        self.put_uint16(len(value))
        self.put_bytes(value)

    def get_bytes(size: int) -> bytes:
        self.ensure_space(size)
        value = bytes(self.data[self.offset : self.offset + size])
        self.offset += size
        self.count = max(self.count, self.offset)
        return value

    def get_uint64() -> int:
        return int.from_bytes(self.get_bytes(8), self.byteorder, signed=False)

    def get_uint32() -> int:
        return int.from_bytes(self.get_bytes(4), self.byteorder, signed=False)

    def get_uint16() -> int:
        return int.from_bytes(self.get_bytes(2), self.byteorder, signed=False)

    def get_byte() -> int:
        return int.from_bytes(self.get_bytes(1), self.byteorder, signed=False)

    def get_int64() -> int:
        return int.from_bytes(self.get_bytes(8), self.byteorder, signed=True)

    def get_int32() -> int:
        return int.from_bytes(self.get_bytes(4), self.byteorder, signed=True)

    def get_int16() -> int:
        return int.from_bytes(self.get_bytes(2), self.byteorder, signed=True)

    def get_signed_byte() -> int:
        return int.from_bytes(self.get_bytes(1), self.byteorder, signed=True)

    def get_string() -> str:
        return self.get_bytes(self.get_uint16()).decode('utf-8')

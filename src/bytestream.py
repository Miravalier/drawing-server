class Bytestream:
    def __init__(self, data: Union[int, bytes, bytearray, None] = None):
        if data is None:
            self.data = bytearray()
        else:
            self.data = bytearray(data)
        self.offset = len(self.data)

    def seek_absolute(self, offset: int) -> int:
        self.offset = max(min(offset, len(self.data)), 0)
        return self.offset

    def seek_relative(self, offset: int) -> int:
        self.offset = max(min(self.offset + offset, len(self.data)), 0)
        return self.offset

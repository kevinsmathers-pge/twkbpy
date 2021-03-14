
from typing import Optional,List
from .constants import GeometryType

class DecoderContext:
    def __init__(self, stream):
        self.stream = stream
        self.refpoint : List[float] = [ 0.0 ]*4
        self.size = 0
        self.ndims : int = 2
        self.type : Optional[GeometryType] = None
        self.factors : List[float] = []
        self.bbox : Optional[List[int]] = None
        self.has_bbox = False
        self.has_size = False
        self.has_idlist = False
        self.has_z = False
        self.has_m = False
        self.is_empty = True
        self.idlist = None

    def byte_gen(self):
        while True:
            b8 = self.stream.read(1)
            if b8 == b'':
                break
            print("read byte",b8)
            yield b8 & 0xff

    def next(self) -> int:
        return self.stream.read(1)[0] & 0xff
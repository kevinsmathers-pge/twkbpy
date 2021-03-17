from .decode import Decoder
from .ogr_transform import OgrTransform
from base64 import b64decode
from io import BytesIO

class Twkb:
    def __init__(self, stream):
        self.decoder = Decoder()
        self.shape = self.decoder.decode(stream)

    @classmethod
    def from_stream(cls, stream):
        return cls(stream)

    @classmethod
    def from_binary(cls, buf):
        stream = BytesIO(buf)
        return cls(stream)

    @classmethod
    def from_b64(cls, b64):
        return cls.from_binary(b64decode(b64))

    def to_geojson(self):
        return self.decoder.to_geojson(self.shape)

    def to_ogr(self):
        xform = OgrTransform()
        return xform.convert(self.shape)


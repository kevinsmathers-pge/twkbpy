# -*- coding: utf-8 -*-
from .decode import Decoder

def decode(stream):
    return Decoder().decode(stream)

def to_geojson(stream):
    _decoder = Decoder()
    geoshape = _decoder.decode(stream)
    return _decoder.to_geojson(geoshape)

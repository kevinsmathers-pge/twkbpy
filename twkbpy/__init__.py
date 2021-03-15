# -*- coding: utf-8 -*-
from .decode import Decoder

def decode(*args):
    return Decoder().decode(*args)

def to_geojson(*args):
    decoder = Decoder()
    return decoder.to_geojson(decoder.decode(*args))

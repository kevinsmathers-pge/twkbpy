# -*- coding: utf-8 -*-
import base64
from .decode import Decoder
from .ogr_transform import OgrTransform

from .twkb import Twkb

def decode(stream):
    return Decoder().decode(stream)

def to_geojson(stream):
    _decoder = Decoder()
    geoshape = _decoder.decode(stream)
    return _decoder.to_geojson(geoshape)

def to_ogr(stream):
    _decoder = Decoder()
    _xform = OgrTransform()
    geoshape = _decoder.decode(stream)
    ogr = _xform.convert(geoshape)
    return ogr

# -*- coding: utf-8 -*-
import itertools

from .constants import GeometryType
from .read_buffer import GeometryShape
from typing import Dict, Any
import json

class JsonFormatter:
    def __init__(self, geom : GeometryShape):
        self.obj = self.xform_geom(geom)

    def to_json(self):
        return json.dumps(self.obj)

    def xform_geom(self, geom : GeometryShape):
        if geom.type == GeometryType.POINT:
            obj = self.xform_point(geom)
        elif geom.type == GeometryType.MULTIPOINT:
            obj = self.xform_multipoint(geom)
        elif geom.type == GeometryType.LINESTRING:
            obj = self.xform_linestring(geom)
        elif geom.type == GeometryType.MULTILINESTRING:
            obj = self.xform_multilinestring(geom)
        elif geom.type == GeometryType.POLYGON:
            obj = self.xform_polygon(geom)
        elif geom.type == GeometryType.MULTIPOLYGON:
            obj = self.xform_multipolygon(geom)
        elif geom.type == GeometryType.COLLECTION:
            obj = self.xform_collection(geom)
        # elif geom.type == GeometryType.FEATURECOLLECTION:
        #     pass
        else:
            raise NotImplementedError(f"{geom.type} not implemented")
        return obj

    def xform_point(self, geom : GeometryShape):
        return create_point(geom.coordinates, geom.ndims)

    def xform_multipoint(self, geom : GeometryShape):
        return create_multipoint(geom.geoms, geom.ids, geom.ndims)

    def xform_linestring(self, geom : GeometryShape):
        return create_linestring(geom.coordinates, geom.ndims)

    def xform_multilinestring(self, geom : GeometryShape):
        return create_multilinestring(geom.geoms, geom.ids, geom.ndims)

    def xform_polygon(self, geom : GeometryShape):
        return create_polygon(geom.coordinates, geom.ndims)

    def xform_multipolygon(self, geom : GeometryShape):
        return create_multipolygon(geom.geoms, geom.ids, geom.ndims)

    def xform_collection(self, geom : GeometryShape):
        return create_collection(geom.geoms, geom.ids, geom.ndims)

type_map = {}
type_map[GeometryType.POINT] = 'Point'
type_map[GeometryType.LINESTRING] = 'LineString'
type_map[GeometryType.POLYGON] = 'Polygon'

def get_type_string(type):
    return type_map[type]

# Create GeoJSON Geometry object from TWKB type and coordinate array
def create_geometry(type, coordinates):
    return {
        'type': get_type_string(type),
        'coordinates': coordinates
    }

def to_coords(coordinates, ndims):
    """
    TWKB flat coordinates to GeoJSON coordinates
    """
    coords = []
    for i in range(0, len(coordinates), ndims):
        pos = []
        for c in range(0, ndims):
            pos.append(coordinates[i + c])
        coords.append(pos)
    return coords


def create_point(coordinates, ndims):
    return create_geometry(GeometryType.POINT, to_coords(coordinates, ndims)[0])


def create_linestring(coordinates, ndims):
    return create_geometry(GeometryType.LINESTRING, to_coords(coordinates, ndims))


def create_polygon(coordinates, ndims):
    coords = [to_coords(c, ndims) for c in coordinates]
    return create_geometry(GeometryType.POLYGON, coords)


def create_feature(type, coordinates, id, ndims):
    feature = {
        'type': 'Feature',
        'geometry': transforms[type](coordinates, ndims)
    }
    if id is not None:
        feature['id'] = id
    return feature

def izip_longest(A, B, fill_value=None):
    a = len(A); b = len(B)
    result = []
    for i in range(0,max(a,b)):
        _a = A[i] if i < a else fill_value
        _b = B[i] if i < b else fill_value
        result.append((a,b))
    return result

def create_features_from_multi(type, geoms, ids, ndims):
    for o in izip_longest(geoms, ids):
        yield create_feature(type, o[0], o[1], ndims)


def create_multipoint(geoms, ids, ndims):
    return create_features_from_multi(GeometryType.POINT, geoms, ids, ndims)


def create_multilinestring(geoms, ids, ndims):
    return create_features_from_multi(GeometryType.LINESTRING, geoms, ids, ndims)


def create_multipolygon(geoms, ids, ndims):
    return create_features_from_multi(GeometryType.POLYGON, geoms, ids, ndims)


def create_features_from_collection(geoms, ids, ndims):
    for o in izip_longest(geoms, ids):
        yield create_feature(o[0]['type'], o[0]['coordinates'], o[1], ndims)


def create_collection(geoms, ids, ndims):
    return create_features_from_collection(geoms, ids, ndims)


transforms = {}
transforms[GeometryType.POINT] = create_point
transforms[GeometryType.LINESTRING] = create_linestring
transforms[GeometryType.POLYGON] = create_polygon
transforms[GeometryType.MULTIPOINT] = create_multipoint
transforms[GeometryType.MULTILINESTRING] = create_multilinestring
transforms[GeometryType.MULTIPOLYGON] = create_multipolygon
transforms[GeometryType.COLLECTION] = create_collection

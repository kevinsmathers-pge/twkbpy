# -*- coding: utf-8 -*-
import itertools

from .constants import GeometryType


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


def create_features_from_multi(type, geoms, ids, ndims):
    for o in itertools.izip_longest(geoms, ids):
        yield create_feature(type, o[0], o[1], ndims)


def create_multipoint(geoms, ids, ndims):
    return create_features_from_multi(GeometryType.POINT, geoms, ids, ndims)


def create_multilinestring(geoms, ids, ndims):
    return create_features_from_multi(GeometryType.LINESTRING, geoms, ids, ndims)


def create_multipolygon(geoms, ids, ndims):
    return create_features_from_multi(GeometryType.POLYGON, geoms, ids, ndims)


def create_features_from_collection(geoms, ids, ndims):
    for o in itertools.izip_longest(geoms, ids):
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

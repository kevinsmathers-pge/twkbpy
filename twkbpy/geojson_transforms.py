# -*- coding: utf-8 -*-
import itertools

from .constants import Constants


type_map = {}
type_map[Constants.POINT] = 'Point'
type_map[Constants.LINESTRING] = 'LineString'
type_map[Constants.POLYGON] = 'Polygon'


# Create GeoJSON Geometry object from TWKB type and coordinate array
def create_geometry(type, coordinates):
    return {
        'type': type_map[type],
        'coordinates': coordinates
    }


# TWKB flat coordinates to GeoJSON coordinates
def to_coords(coordinates, ndims):
    coords = []
    for i in range(0, len(coordinates), ndims):
        pos = []
        for c in range(0, ndims):
            pos.append(coordinates[i + c])
        coords.append(pos)
    return coords


def create_point(coordinates, ndims):
    return create_geometry(Constants.POINT, to_coords(coordinates, ndims)[0])


def create_linestring(coordinates, ndims):
    return create_geometry(Constants.LINESTRING, to_coords(coordinates, ndims))


def create_polygon(coordinates, ndims):
    coords = [to_coords(c, ndims) for c in coordinates]
    return create_geometry(Constants.POLYGON, coords)


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
    return create_features_from_multi(Constants.POINT, geoms, ids, ndims)


def create_multilinestring(geoms, ids, ndims):
    return create_features_from_multi(Constants.LINESTRING, geoms, ids, ndims)


def create_multipolygon(geoms, ids, ndims):
    return create_features_from_multi(Constants.POLYGON, geoms, ids, ndims)


def create_features_from_collection(geoms, ids, ndims):
    for o in itertools.izip_longest(geoms, ids):
        yield create_feature(o[0]['type'], o[0]['coordinates'], o[1], ndims)


def create_collection(geoms, ids, ndims):
    return create_features_from_collection(geoms, ids, ndims)


transforms = {}
transforms[Constants.POINT] = create_point
transforms[Constants.LINESTRING] = create_linestring
transforms[Constants.POLYGON] = create_polygon
transforms[Constants.MULTIPOINT] = create_multipoint
transforms[Constants.MULTILINESTRING] = create_multilinestring
transforms[Constants.MULTIPOLYGON] = create_multipolygon
transforms[Constants.COLLECTION] = create_collection

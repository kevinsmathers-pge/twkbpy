# -*- coding: utf-8 -*-
import itertools

from .constants import GeometryType
from .read_buffer import GeometryShape
from typing import Dict, Any, List, Optional
import json

class JsonFormatter:
    def __init__(self, geom : GeometryShape):
        self.obj = self.xform_geom(geom)

    def get_type_string(self, _type):
        result = None
        if _type == GeometryType.POINT:
            result = "Point"
        elif _type == GeometryType.LINESTRING:
            result = "LineString"
        elif _type == GeometryType.POLYGON:
            result = "Polygon"
        else:
            raise ValueError(f"Unsupported geometry type {_type}")
        return result

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
        return self.create_point(geom.coordinates, geom.ndims)

    def xform_linestring(self, geom : GeometryShape):
        return self.create_linestring(geom.coordinates, geom.ndims)

    def xform_multipoint(self, geom : GeometryShape):
        return self.create_multipoint(geom.geoms, geom.ids, geom.ndims)

    def xform_multilinestring(self, geom : GeometryShape):
        return self.create_multilinestring(geom.geoms, geom.ids, geom.ndims)

    def xform_polygon(self, geom : GeometryShape):
        return self.create_polygon(geom.coordinates, geom.ndims)

    def xform_multipolygon(self, geom : GeometryShape):
        return self.create_multipolygon(geom.geoms, geom.ids, geom.ndims)

    def xform_collection(self, geom : GeometryShape):
        return self.create_collection(geom.geoms, geom.ids, geom.ndims)

    def create_geometry(self, _type : GeometryType, coordinates : List[float], ndims : int):
        return {
            'type': self.get_type_string(_type),
            'coordinates': self.to_coords(coordinates, ndims)
        }

    @staticmethod
    def at(A, i:int):
        if i < len(A):
            return A[i]
        return None

    def create_feature(self, _type : GeometryType, geom : Optional[GeometryShape], id : Optional[int], ndims : int):
        assert(ndims != 0)
        assert(not geom is None)
        assert(_type == geom.type)
        geomjson = None
        if geom.type == GeometryType.POINT:
            geomjson = self.create_point(geom.coordinates, ndims)
        elif geom.type == GeometryType.LINESTRING:
            geomjson = self.create_linestring(geom.coordinates, ndims)
        elif geom.type == GeometryType.POLYGON:
            geomjson = self.create_polygon(geom.coordinates, ndims)
        elif geom.type == GeometryType.MULTIPOINT:
            geomjson = self.create_multipoint(geom.geoms, geom.ids, ndims)
        elif geom.type == GeometryType.MULTILINESTRING:
            geomjson = self.create_multilinestring( geom.geoms, geom.ids, ndims)
        elif geom.type == GeometryType.MULTIPOLYGON:
            geomjson = self.create_multipolygon(geom.geoms, geom.ids, ndims)
        elif geom.type == GeometryType.COLLECTION:
            geomjson = self.create_collection(geom.geoms, geom.ids, ndims)
        else:
            raise NotImplementedError(f"Unimplemented geometry type {geom.type}")

        feature = {
            'type': 'Feature',
            'geometry': geomjson
        }
        if id is not None:
            feature['id'] = id
        return feature

    def create_features_from_multi(self, _type : GeometryType, geoms : List[GeometryShape], ids : List[int], ndims : int):
        n = max([len(geoms), len(ids)])
        result = []
        for i in range(0,n):
            geo : Optional[GeometryShape] = self.at(geoms, i)
            gid : Optional[int] = self.at(ids, i)
            result.append( self.create_feature(_type, geo, gid, ndims))
        return result

    def to_coords(self, coordinates : List[float], ndims : int):
        """
        TWKB flat coordinates to GeoJSON coordinates
        """
        coords = []
        assert(ndims != 0)
        for i in range(0, len(coordinates), ndims):
            pos = []
            for c in range(0, ndims):
                pos.append(coordinates[i + c])
            coords.append(pos)
        return coords

    def create_point(self, coordinates : List[float], ndims):
        assert(ndims != 0)
        return self.create_geometry(GeometryType.POINT, self.to_coords(coordinates, ndims)[0], ndims)

    def create_linestring(self, coordinates : List[float], ndims):
        assert(ndims != 0)
        return self.create_geometry(GeometryType.LINESTRING, self.to_coords(coordinates, ndims), ndims)


    def create_polygon(self, coordinates : List[float], ndims):
        assert(ndims != 0)
        coords = self.to_coords(coordinates, ndims)
        return self.create_geometry(GeometryType.POLYGON, coords, ndims)


    def create_multipoint(self, geoms : List[GeometryShape], ids : List[int], ndims : int):
        assert(ndims != 0)
        return self.create_features_from_multi(GeometryType.POINT, geoms, ids, ndims)


    def create_multilinestring(self, geoms : List[GeometryShape], ids : List[int], ndims : int):
        assert(ndims != 0)
        return self.create_features_from_multi(GeometryType.LINESTRING, geoms, ids, ndims)


    def create_multipolygon(self, geoms : List[GeometryShape], ids : List[int], ndims : int):
        assert(ndims != 0)
        return self.create_features_from_multi(GeometryType.POLYGON, geoms, ids, ndims)

    def create_features_from_collection(self, geoms : List[GeometryShape], ids : List[int], ndims : int):
        assert(ndims != 0)
        n = max([len(geoms), len(ids)])
        result = []
        for i in range(0,n):
            geo : Optional[GeometryShape] = self.at(geoms, i)
            gid : Optional[int] = self.at(ids, i)
            result.append( self.create_feature(geo.type, geo, gid, ndims))
        return result

    def create_collection(self, geoms : List[GeometryShape], ids : List[int], ndims : int):
        assert(ndims != 0)
        return self.create_features_from_collection(geoms, ids, ndims)




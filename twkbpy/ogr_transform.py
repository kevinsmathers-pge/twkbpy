
from sys import getrecursionlimit
from typing import Coroutine
from .read_buffer import GeometryShape, GeometryType
from osgeo import ogr

class OgrTransform:
    def __init__(self):
        pass

    def convert(self, shape : GeometryShape) -> ogr.Geometry:
        return self.xform_shape(shape, shape.ndims)

    def xform_shape(self, shape : GeometryShape, ndims : int) -> ogr.Geometry:
        t = shape.type
        if t == GeometryType.MULTILINESTRING:
            geom = self.xform_multilinestring(shape, ndims)
        elif t == GeometryType.LINESTRING:
            geom = self.xform_line(shape, ndims)
        elif t == GeometryType.MULTIPOINT:
            geom = self.xform_multipoint(shape, ndims)
        elif t == GeometryType.POINT:
            geom = self.xform_point(shape, ndims)
        # elif t == GeometryType.POLYGON:
        #     geom = self.xform_polygon(shape, ndims)
        else:
            raise NotImplementedError(f"Unimplemented type {t}")
        return geom

    def xform_polygon(self, shape : GeometryShape, ndims : int) -> ogr.Geometry:
        assert(shape.type == GeometryType.POLYGON)
        geom = ogr.Geometry(ogr.wkbPolygon)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        # TODO
        

    def xform_multilinestring(self, shape : GeometryShape, dims : int) -> ogr.Geometry:
        assert(shape.type == GeometryType.MULTILINESTRING)
        geom = ogr.Geometry(ogr.wkbMultiLineString)
        for i in range(0,len(shape.geoms)):
            o = self.xform_line(shape.geoms[i], dims)
            geom.AddGeometry(o)
        return geom

    @staticmethod
    def fill_points(shape : GeometryShape, geom : ogr.Geometry, dims : int):
        for i in range(0,len(shape.coordinates),dims):
            x = shape.coordinates[i+0]
            y = shape.coordinates[i+1]
            z = 0
            if dims > 2:
                z = shape.coordinates[i+2]
            geom.AddPoint(x, y, z)        

    def xform_line(self, shape : GeometryShape, dims : int) -> ogr.Geometry:
        assert(shape.type == GeometryType.LINESTRING)
        geom = ogr.Geometry(ogr.wkbLineString)
        self.fill_points(shape, geom, dims)
        return geom

    def xform_point(self, shape : GeometryShape, dims : int) -> ogr.Geometry:
        assert(shape.type == GeometryType.POINT)
        geom = ogr.Geometry(ogr.wkbMultiPoint)
        self.fill_points(shape, geom, dims)
        return geom

    def xform_multipoint(self, shape : GeometryShape, dims : int) -> ogr.Geometry:
        assert(shape.type == GeometryType.MULTIPOINT)
        geom = ogr.Geometry(ogr.wkbPoint)
        for i in range(0,len(shape.geoms)):
            o = self.xform_point(shape.geoms[i], dims)
            geom.AddGeometry(o)
        return geom
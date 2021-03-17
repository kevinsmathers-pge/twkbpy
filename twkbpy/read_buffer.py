import math
from typing import Callable, List, Any, Optional
from dataclasses import dataclass

from .context import DecoderContext
from .constants import GeometryType
from .protobuf import unzigzag, read_varsint64, read_varint64
from .context import DecoderContext

class GeometryShape:
    def __init__(self, 
            type : GeometryType, 
            dims : Optional[List[int]] = None, 
            ids : Optional[List[int]] = None, 
            geoms : Optional[List[Any]] = None, 
            coordinates : Optional[List[float]] = None,
            ndims : Optional[int] = None
            ) :
        self.type = type
        if not dims is None:
           self.dims = dims
        if not ids is None:
            self.ids = ids
        if not geoms is None:
            self.geoms = geoms
        if not coordinates is None:
            self.coordinates = coordinates
        if not ndims is None:
            self._ndims = ndims

    @property
    def ndims(self):
        return self._ndims

    @ndims.setter
    def ndims(self, value : int):
        self._ndims = value

DEBUG=False

def read_pa(ta_struct : DecoderContext, npoints : int) -> List[float]:
    """
    Reads an array of delta compressed integers from the decoder context
    and scales them back into coordinates

    Returns:
        coords : List[float]
    """
    if DEBUG:
        print("read_pa")
    ndims = ta_struct.ndims
    assert(ndims != 0)
    factors = ta_struct.factors
    coords = [0.0] * (npoints * ndims)

    for i in range(0, npoints):
        for j in range(0, ndims):
            ta_struct.refpoint[j] += read_varsint64(ta_struct)
            coords[ndims * i + j] = ta_struct.refpoint[j] / factors[j]

    '''
    # calculates the bbox if it hasn't it
    if (ta_struct.include_bbox && !ta_struct.has_bbox) {
      for (i = 0; i < npoints; i++) {
        for (j = 0; j < ndims; j++) {
          var c = coords[j * ndims + i]
          if (c < ta_struct.bbox.min[j]) {
            ta_struct.bbox.min[j] = c
          }
          if (c > ta_struct.bbox.max[j]) {
            ta_struct.bbox.max[j] = c
          }
        }
      }
    }
    '''
    return coords


def read_id_list(ta_struct : DecoderContext, n : int) -> List[int]:
    """
    Reads a list of IDs
    """
    if DEBUG:
        print("read_id_list")
    id_list = []
    for _i in range(0, n):
        id_list.append(read_varsint64(ta_struct))
    return id_list


def parse_point(ta_struct : DecoderContext) -> GeometryShape:
    """
    Reads and parses the bytes for a single point

    Returns:
        GeometryShape - coordinates for the single point that was read
    """
    if DEBUG:
        print("parse_point")
    return GeometryShape(type = GeometryType.POINT, coordinates = read_pa(ta_struct, 1))


def parse_line(ta_struct : DecoderContext) -> GeometryShape:
    """
    Reads and parses bytes that form a polyline

    Returns:
        GeometryShape - coordinates for a piecewise linear series of points
    """
    if DEBUG:
        print("parse_line")
    _type = GeometryType.LINESTRING
    npoints = read_varint64(ta_struct)
    coords = read_pa(ta_struct, npoints)
    if DEBUG:
        print(f"parse_line -> {_type},{coords}")
    return GeometryShape(type = _type, coordinates = coords)

def parse_polygon(ta_struct : DecoderContext) -> GeometryShape:
    """
    Reads and parses bytes the form a polygon

    Returns:
        GeometryShape - coordinates for a series of polygon rings
    """
    if DEBUG:
        print("parse_polygon")
    coords = []
    nrings = read_varint64(ta_struct)
    for _ring in range(0, nrings):
        coords.append(parse_line(ta_struct))
    return GeometryShape(type = GeometryType.POLYGON, coordinates = coords)

def parse_multi(ta_struct : DecoderContext, 
                parser : Callable[[DecoderContext], GeometryShape]) -> GeometryShape :
    """
    Reads and parses bytes that form a multi-entity geometry
    """
    if DEBUG:
        print("parse_multi")
    if ta_struct.type is None: raise ValueError("Can't parse unknown type")
    _type = ta_struct.type
    ngeoms = read_varint64(ta_struct)
    geoms : List[GeometryShape] = []
    id_list = []
    if ta_struct.has_idlist:
        id_list = read_id_list(ta_struct, ngeoms)

    for _i in range(0, ngeoms):
        geo = parser(ta_struct)
        geoms.append(geo)

    if DEBUG:
        print(f"parse_multi -> {_type},{id_list},{geoms}")
    return GeometryShape(
        type=_type,
        ids=id_list,
        geoms=geoms
    )

def parse_collection(ta_struct : DecoderContext) -> GeometryShape:
    if DEBUG:
        print("parse_collection")
    if ta_struct.type is None: raise ValueError("Can't parse unknown type")
    geom_type = ta_struct.type
    ngeoms = read_varint64(ta_struct)
    geoms : List[GeometryShape] = []
    id_list = []
    if ta_struct.has_idlist:
        id_list = read_id_list(ta_struct, ngeoms)

    for _i in range(0, ngeoms):
        geo = read_buffer(ta_struct)
        geoms.append(geo)

    shape = GeometryShape(
        type = geom_type,
        ids = id_list,
        geoms = geoms,
        ndims = ta_struct.ndims
    )
    return shape

def read_objects(ta_struct : DecoderContext) -> GeometryShape:
    if DEBUG:
        print("read_objects")
    type = ta_struct.type
    for i in range(0, ta_struct.ndims + 1):
        ta_struct.refpoint[i] = 0

    if type == GeometryType.POINT:
        return parse_point(ta_struct)

    if type == GeometryType.LINESTRING:
        return parse_line(ta_struct)

    if type == GeometryType.POLYGON:
        return parse_polygon(ta_struct)

    if type == GeometryType.MULTIPOINT:
        return parse_multi(ta_struct, parse_point)

    if type == GeometryType.MULTILINESTRING:
        return parse_multi(ta_struct, parse_line)

    if type == GeometryType.MULTIPOLYGON:
        return parse_multi(ta_struct, parse_polygon)

    if type == GeometryType.COLLECTION:
        return parse_collection(ta_struct)

    raise TypeError('Unknown type: %s' % type)


def read_buffer(ta_struct : DecoderContext) -> GeometryShape:
    if DEBUG:
        print("read_buffer")
    has_z = 0
    has_m = 0

    flag = ta_struct.next()

    precision_xy = unzigzag((flag & 0xF0) >> 4)
    ta_struct.type = GeometryType(flag & 0x0F)
    ta_struct.factors = [ 0.0 ] * 4
    precision_xy = math.pow(10, precision_xy)
    ta_struct.factors[0] = precision_xy
    ta_struct.factors[1] = precision_xy

    if DEBUG: 
        print(f" - precision_xy = {precision_xy}")
        print(f" - type = {ta_struct.type}")

    # Metadata header
    flag = ta_struct.next()

    ta_struct.has_bbox = ((flag & 0x01) != 0)
    ta_struct.has_size = ((flag & 0x02) != 0)
    ta_struct.has_idlist = ((flag & 0x04) != 0)
    ta_struct.is_empty = ((flag & 0x10) != 0)

    if DEBUG:
        print(f" - has_bbox = {ta_struct.has_bbox}")
        print(f" - has_size = {ta_struct.has_size}")
        print(f" - has_idlist = {ta_struct.has_idlist}")
        print(f" - is_empty = {ta_struct.is_empty}")

    extended_dims = (flag & 0x08) != 0

    # the geometry has Z and/or M coordinates
    if extended_dims:
        extended_dims_flag = ta_struct.next()

        # Strip Z/M presence and precision from ext byte
        has_z = (extended_dims_flag & 0x01) != 0
        has_m = (extended_dims_flag & 0x02) != 0
        precision_z = (extended_dims_flag & 0x1C) >> 2
        precision_m = (extended_dims_flag & 0xE0) >> 5

        # Convert the precision into factor
        if has_z:
            ta_struct.factors[2] = math.pow(10, precision_z)
        if has_m:
            ta_struct.factors[2 + has_z] = math.pow(10, precision_m)
        # store in the struct
        ta_struct.has_z = has_z
        ta_struct.has_m = has_m

    ndims = 2 + has_z + has_m
    ta_struct.ndims = ndims

    if ta_struct.has_size:
        ta_struct.size = read_varint64(ta_struct)

    if ta_struct.has_bbox:
        bbox = [ 0 ] * (ndims * 2)
        for i in range(0, ndims):
            min = read_varsint64(ta_struct)
            max = min + read_varsint64(ta_struct)
            bbox[i] = min
            bbox[i + ndims] = max
        ta_struct.bbox = bbox

    gshape = read_objects(ta_struct)
    gshape.ndims = ta_struct.ndims
    return gshape

# -*- coding: utf-8 -*-
from enum import Enum

class GeometryType(Enum):
    POINT = 1
    LINESTRING = 2
    POLYGON = 3
    MULTIPOINT = 4
    MULTILINESTRING = 5
    MULTIPOLYGON = 6
    COLLECTION = 7

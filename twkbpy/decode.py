# -*- coding: utf-8 -*-

from .geojson_transforms import transforms
from .read_buffer import read_buffer
from .context import DecoderContext


class Decoder:
    def __init__(self):
        pass

    def xdecode(self, stream):
        print("decode")
        ta_struct = DecoderContext(stream)
        features = []

        shape = read_buffer(ta_struct)
        print(shape)
        #for res in read_buffer(ta_struct):
        #    pass
        #     ndims = ta_struct.ndims
        #     if 'geoms' in res:
        #         transformer = transforms[res['type']]
        #         for feature in transformer(res['geoms'], res['ids'], ndims):
        #             yield feature
    #         else:
    #             ''
    #             transformer = transforms[ta_struct.type]
    #             yield {
    #                 'type': 'Feature',
    #                 'geometry': transformer(res, ndims)
    #             }

    # def to_geojson(self, stream):
    #     features = [f for f in self.decode(stream)]
    #     return {
    #         'type': 'FeatureCollection',
    #         'features': features
    #     }

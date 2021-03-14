# -*- coding: utf-8 -*-
from twkbpy.context import DecoderContext

def unzigzag(n_val : int) -> int:
    """
    Converts unsigned zigzag encoded int to signed int
    """
    if (n_val & 1) == 0:
        return n_val >> 1
    return -(n_val >> 1) - 1

def read_varint64(ta_struct : DecoderContext) -> int:
    """
    Read unsigned variable length integer
    """
    #print("read_varint64")
    #cursor = ta_struct['cursor']
    n_val = 0
    n_shift = 0
    result = 0
    while True:
        n_byte = ta_struct.next()
        if (n_byte & 0x80) == 0:
            #cursor += 1
            #ta_struct['cursor'] = cursor
            result = n_val | (n_byte << n_shift)
            break
        n_val = n_val | (n_byte & 0x7f) << n_shift
        #cursor += 1
        n_shift += 7
    return result


def read_varsint64(ta_struct : DecoderContext) -> int:
    """
    Read signed variable length integer from zigzag encoded bytes
    """
    #print("read_varsint64")
    n_val = read_varint64(ta_struct)
    return unzigzag(n_val)

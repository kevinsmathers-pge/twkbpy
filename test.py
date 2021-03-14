import io
import twkbpy as twkb

def hex_to_bytes(hex_str):
    bytes = []
    hex_str = ''.join(hex_str.split(' '))

    for i in range(0, len(hex_str), 2):
        bytes.append(int(hex_str[i:i + 2], 16))
    return bytes


def byte_gen(stream):
    while True:
        a = stream.read(1)
        if a == b'':
            break
        yield bytearray(a)[0]

#import pdb; pdb.set_trace()
print("start")
codec = twkb.Decoder()
with io.open('komm.twkb', 'rb') as stream:   
    codec.xdecode(stream)
print("end")
#print bytearray(stream.read(1))[0]
#for b in stream:
#    data = bytearray(b)
#    print data[0]

'''
raw_bytes = stream.getvalue()
print(len(raw_bytes))
print(type(raw_bytes))
'''
'''
print barr

print type(barr)
for c in barr:
    print c

stream = io.BytesIO(barr)

print type(stream.getvalue())

for d in stream.getvalue():
    print type(d)
'''

#print len(bytes('01000204'))
#for b in bytearray.fromhex('01000204'):
#    print b

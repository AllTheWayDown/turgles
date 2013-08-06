from cffi import FFI
ffi = FFI()


TURTLE_DATA_SIZE = 12
# x
# y
# scale x
# scale y
# degrees
# speed
# st
# ct
# r
# g
# b
# a


def create_turtle_buffer(size):
    return ffi.new('float[%s]' % (size * TURTLE_DATA_SIZE))


def create_index_buffer(init):
    """indexes of vertex triangles"""
    return ffi.new('unsigned short[]', init)


def create_vertex_buffer(init):
    """vec4 array"""
    return ffi.new('float[]', init)


def to_pointer(ctype):
    #TODO support 32bit systems?
    return int(ffi.cast('long', ctype))


def create_matrix():
    return ffi.new('float[16]')

# short cut
sizeof = ffi.sizeof

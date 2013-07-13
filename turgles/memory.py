from cffi import FFI
ffi = FFI()


TURTLE_DATA_SIZE = 8

def create_turtle_buffer(init):
    assert len(init) % TURTLE_DATA_SIZE == 0
    return ffi.new('float[]', init)

def create_index_buffer(init):
    """indexes of vertex triangles"""
    assert len(init) % 3 == 0
    return ffi.new('unsigned short[]', init)

def create_vertex_buffer(init):
    """vec4 array"""
    assert len(init) % 4 == 0
    return ffi.new('float[]', init)

def to_pointer(ctype):
    #TODO support 32bit systems?
    return int(ffi.cast('long', ctype))

# short cut
size_in_bytes = ffi.sizeof

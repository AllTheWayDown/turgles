import ctypes
from cffi import FFI
ffi = FFI()


# Turgles uses 2 types of rendering - pseudo-instancing for ES2, and hardware
# instancing for everything else. We want to use tightly packed contiguous
# memory layout for a) easy upload to VBO for hardware instancing b) model
# acceleration in C code and c) it facilitates zero-copy rendering.
#
# However, pseudo instancing requires using uniform arrays for ES2, rather
# than attributes. And multiple uniform arrays are *not* contiguous (and ES2
# doesn't support Uniform Buffer Objects). So we'd have to all the turtle data
# into non-contiguous blocks *every frame*, losing our zero-copy. And this is
# the slower ES2 case, so we're already hurting.
#
# One solution is to have different memory layouts for ES2 renderers to normal,
# but this is messy and affects model acceleration also.
#
# The other solution is to have a single large uniform array that can be
# set from a contiguous memory block. This preserves the same memory layout and
# zero-copy rendering as the non-ES case.  This is has the downside of wasted
# space, as we'd need to use the next size of variable up from the number of
# items we need. So we'll use a little more GPU bandwidth to avoid copying in
# main memory. Given our GPU bandwidth requirements are low, this is not an
# issue. Also, given the largest type available is mat4, 16 floats is a much as
# we can have per-turtle-per-contiguous-array.
#
# So, the memory layouts below are larger that they need to be, with some
# currently unused space, which will be copied up to the GPU each frame. But at
# least there's some spare space if we need to add new things.

# We need 11 floats currently, so use mat4
TURTLE_MODEL_DATA_SIZE = 16

# 0:  x position
# 1:  y position
# 2:  x scale
# 3:  y scale
# 4:  heading angle (degrees)
# 5:  orientation angle (degrees)
# 6:  cos of heading angle
# 7:  sin of heading angle
# 8:  cos of orientation angle
# 9:  sin of orientation angle
# 10: speed
# 11: unused
# 12: unused
# 13: unused
# 14: unused
# 15: unused


# We need 9, so use mat3
TURTLE_COLOR_DATA_SIZE = 9
# 0: pen r
# 1: pen g
# 2: pen b
# 6: pen alpha
# 3: fill r
# 4: fill g
# 5: fill b
# 7: fill alpha
# 8: pen thickness


def create_turtle_position_buffer(size):
    return ffi.new('float[%s]' % (size * TURTLE_MODEL_DATA_SIZE))


def create_turtle_color_buffer(size):
    return ffi.new('float[%s]' % (size * TURTLE_COLOR_DATA_SIZE))


def create_index_buffer(init):
    """indexes of vertex triangles"""
    return ffi.new('unsigned short[]', init)


def create_vertex_buffer(init):
    """vec4 array"""
    return ffi.new('float[]', init)


def to_raw_pointer(data):
    """Returns the address in memory as an int for ffi cdata"""
    #TODO support 32bit systems?
    return int(ffi.cast('long', data))


def to_float_pointer(data):
    return ctypes.pointer(ctypes.c_float.from_address(to_raw_pointer(data)))


def to_int_pointer(data):
    return ctypes.pointer(ctypes.c_int.from_address(to_raw_pointer(data)))


def create_matrix():
    return ffi.new('float[16]')

# short cut
sizeof = ffi.sizeof

from __future__ import division, print_function, absolute_import

from random import random
from math import radians, sin, cos

from turgles.config import speed, degrees, world_width, world_height
from turgles.memory import ffi, TURTLE_MODEL_DATA_SIZE

half_w = world_width // 2
half_h = world_height // 2

ffi.cdef(
    "void random_walk_all(float*, int, float, float, float, float);"
)
try:
    fast = ffi.dlopen('./libfast.so')
except:
    fast = None


def slow_update(dt, buffers):
    magnitude = speed * dt
    for b in buffers:
        walk(b.model.data, b.count, magnitude, half_w, degrees)

if fast:
    def fast_update(dt, buffers):
        magnitude = speed * dt
        for b in buffers:
            fast.random_walk_all(
                b.model.data, b.count, magnitude, half_w, half_h, degrees)
    update = fast_update
else:
    update = slow_update


def walk(data, size, magnitude, scale, degress):
    for x in range(0, size * TURTLE_MODEL_DATA_SIZE, TURTLE_MODEL_DATA_SIZE):
        y = x + 1
        a = x + 4
        angle = data[a]
        absx, absy = abs(data[x]), abs(data[y])
        if absx > half_h or absy > half_w:
            angle = (angle + 180) % 360
        angle += (random() * 2 * degrees) - degrees
        theta = radians(angle)
        ct = cos(theta)
        st = sin(theta)
        dx = magnitude * ct
        dy = magnitude * st
        data[x] += dx
        data[y] += dy
        data[a] = angle
        data[x + 6] = ct
        data[x + 7] = st

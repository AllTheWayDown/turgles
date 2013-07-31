from __future__ import division, print_function, absolute_import

from random import random
from math import radians, sin, cos

from turgles.config import speed, degrees, half_size
from turgles.memory import ffi


ffi.cdef(
    "void random_walk_all(float*, int, float, float, float, float);"
)
fast = ffi.dlopen('./libfast.so')

turtle_data_size = 8


def fast_update(dt, buffers):
    magnitude = speed * dt
    for b in buffers:
        fast.random_walk_all(
            b.data, b.count, magnitude, half_size, 0.0, degrees)


def slow_update(dt, buffers):
    magnitude = speed * dt
    for b in buffers:
        walk(b.data, b.count, magnitude, half_size, degrees)


def walk(data, size, magnitude, scale, degress):
    for x in range(0, size * turtle_data_size, turtle_data_size):
        y = x + 1
        a = x + 4
        angle = data[a]
        absx, absy = abs(data[x]), abs(data[y])
        if absx > half_size or absy > half_size:
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

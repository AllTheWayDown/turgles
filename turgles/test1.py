from __future__ import division, print_function, absolute_import

from random import randint, random, expovariate

from math import radians, sin, cos, pi
from time import time
import pyglet
from ctypes import sizeof


from turgles.renderer import BaseRenderer, Renderer
from turgles.gles20 import *
from turgles.shader import *
from turgles.util import measure

from turgles.config import *
from memory import ffi, create_turtle_buffer

ffi.cdef(
    "void random_walk_all(float*, int, float, float, float, float);"
)
fast = ffi.dlopen('./libfast.so')

# world coords
turtle_data_size = 8
def gen_world():
    for i in range(num_turtles):
        degrees = random() * 360.0
        t = radians(degrees)
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield turtle_size  # * random() + 1.0
        yield turtle_size  # * random() + 1.0
        yield degrees
        yield 0.0
        yield cos(t)
        yield sin(t)


turtle_model = create_turtle_buffer(list(gen_world()))

renderer = Renderer(world_size, world_size, shape, samples=16)

@renderer.window.event
def on_draw():
    renderer.render(turtle_model, num_turtles)

def u1(dt):
    with measure("update"):
        magnitude = speed * dt
        fast.random_walk_all(
            turtle_model, num_turtles, magnitude, half_size, 0.0, degrees
        )

def update(dt):
    with measure("update"):
        magnitude = speed * dt
        for x in range(0, num_turtles * turtle_data_size, turtle_data_size):
            y = x + 1
            a = x + 4
            angle = turtle_model[a]
            if (abs(turtle_model[x]) > half_size or
                abs(turtle_model[y]) > half_size):
                angle = (angle + 180) % 360
            angle += (random() * 2 * degrees) - degrees
            theta = radians(angle)
            ct = cos(theta)
            st = sin(theta)
            dx = magnitude * ct
            dy = magnitude * st
            turtle_model[x] += dx
            turtle_model[y] += dy
            turtle_model[a] = angle
            turtle_model[x + 6] = ct
            turtle_model[x + 7] = st


def idle():
    self = pyglet.app.event_loop
    app = pyglet.app
    dt = self.clock.update_time()
    redraw_all = self.clock.call_scheduled_functions(dt)

    # Redraw all windows
    for window in app.windows:
        if redraw_all or (window._legacy_invalid and window.invalid):
            with measure("full draw"):
                window.switch_to()
                window.dispatch_event('on_draw')
                with measure("flip"):
                    window.flip()
                window._legacy_invalid = False

    # Update timout
    return self.clock.get_sleep_time(True)

pyglet.clock.schedule_interval(u1, 1/30)
pyglet.app.event_loop.idle = idle
pyglet.app.run()

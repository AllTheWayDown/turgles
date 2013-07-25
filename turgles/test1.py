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
from turgles.memory import ffi, create_turtle_buffer
from turgles.random_walk import fast_update, slow_update


def gen_world(n):
    for i in range(n):
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


renderer = Renderer(world_size, world_size, samples=16)

turtle_model_b = create_turtle_buffer(list(gen_world(num_turtles // 2)))
turtle_model_a = create_turtle_buffer(list(gen_world(num_turtles // 2)))
buffers = (
    ('turtle', turtle_model_a, num_turtles // 2),
    ('triangle', turtle_model_b, num_turtles // 2),
)


@renderer.window.event
def on_draw():
    renderer.render(buffers)


def update(dt):
    with measure("update"):
        fast_update(dt, buffers)


# patch idle func to measure full draw time
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

pyglet.clock.schedule_interval(update, 1/30)
pyglet.app.event_loop.idle = idle
pyglet.app.run()

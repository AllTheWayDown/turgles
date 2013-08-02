from __future__ import division, print_function, absolute_import
import logging

logging.basicConfig()

from random import random
from math import radians, cos, sin
import pyglet

from turgles.renderer import Renderer
from turgles.util import measure

from turgles.config import (
    world_size,
    half_size,
    num_turtles,
    turtle_size,
)
from turgles.random_walk import fast_update


def gen_world(n):
    for i in range(n):
        d = random() * 360.0
        t = radians(d)
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield turtle_size  # * random() + 1.0
        yield turtle_size  # * random() + 1.0
        yield d
        yield 0.0
        yield cos(t)
        yield sin(t)
        yield random()  # r
        yield random()  # g
        yield random()  # b
        yield 1.0       # alpha


half_turtles = num_turtles // 2
renderer = Renderer(
    world_size,
    world_size,
    samples=16,
)


for i in range(half_turtles):
    renderer.create_turtle_data('turtle', list(gen_world(1)))

for i in range(half_turtles):
    renderer.create_turtle_data('classic', list(gen_world(1)))


@renderer.window.event
def on_draw():
    renderer.render()


def update(dt):
    with measure("update"):
        fast_update(dt, renderer.manager.buffers.values())


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

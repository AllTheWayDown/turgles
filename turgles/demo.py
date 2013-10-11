from __future__ import division, print_function, absolute_import
import logging
import sys

logging.basicConfig()

from random import random, choice
from math import radians, cos, sin
import pyglet

# TODO detect supported features and choose automatically
# simpler more compliant renderer
from turgles.es_renderer import ES2Renderer as Renderer
# more powerful modern opengl renderer
#from turgles.renderer import Renderer

from turgles.util import measure

from turgles.config import (
    world_width,
    world_height,
    num_turtles,
    turtle_size,
)
from turgles.random_walk import update as _update

if len(sys.argv) > 1:
    num_turtles = int(sys.argv[1])
if len(sys.argv) > 2:
    turtle_size = float(sys.argv[2])


def gen_turtle():
    d = random() * 360.0
    t = radians(d)
    r, g, b = random(), random(), random()
    return [
        random() * world_width - world_width//2,
        random() * world_height - world_height//2,
        turtle_size,  # * random() + 1.0
        turtle_size,  # * random() + 1.0
        d,  # heading
        d,  # orientation
        cos(t),  # cos(heading)
        sin(t),  # sin(heading)
        cos(t),  # cos(orientation)
        sin(t),  # sin(orientation)
        3.0,    # speed
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        r,
        g,
        b,
        1.0,       # alpha
        1-r,
        1-g,
        1-b,
        1.0,       # alpha
        1.0,       # width
    ]


shapes = [
    'turtle',
    'classic',
    'square',
    'circle',
    'triangle',
    'arrow',
]

n, m = divmod(num_turtles, len(shapes))

renderer = Renderer(
    world_width,
    world_height,
    buffer_size=num_turtles,
)


class Model(object):
    pass

ID = 0
for shape in shapes:
    for i in range(n):
        model = Model()
        model.id = ID
        renderer.create_turtle(model, gen_turtle(), shape)
        ID += 1

extra_shapes = choice(shapes)
for i in range(m):
    model = Model()
    model.id = ID
    renderer.create_turtle(model, gen_turtle(), shape)
    ID += 1


@renderer.window.event
def on_draw():
    with measure('render'):
        renderer.render(flip=False)


def update(dt):
    with measure("update"):
        _update(dt, renderer.manager.buffers.values())


_flip = renderer.window.flip


def flip():
    with measure('flip'):
        _flip()

renderer.window.flip = flip

pyglet.clock.schedule_interval(update, 1/30)
pyglet.app.run()

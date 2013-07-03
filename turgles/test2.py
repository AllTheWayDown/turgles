from __future__ import division, print_function, absolute_import

from random import randint, random, expovariate

from math import radians, sin, cos, pi
from time import time
import pyglet
from ctypes import sizeof

from array import array

from renderer import TurGLESRenderer
from util import measure
world_size = 800.0
half_size = world_size / 2
turtle_size = 10.0
num_turtles = 10000
shape = 'turtle'

# world coords
turtle_data_size = 4
def gen_world():
    for i in range(num_turtles):
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield random() * 360.0
        yield turtle_size  # * random() + 1.0

turtle_model = array('f', list(gen_world())) #, lock=False)

renderer = TurGLESRenderer(world_size, world_size)

@renderer.window.event
def on_draw():
    renderer.render(turtle_model)

speed = 50.0
degrees = 15.0
lambd = 1.0 / degrees
half_degrees = degrees / 2


def update(dt):
    with measure("update"):
        magnitude = speed * dt
        for x in range(0, num_turtles * turtle_data_size, turtle_data_size):
            y = x + 1
            angle = turtle_model[x + 2]
            if (abs(turtle_model[x]) > half_size or
                abs(turtle_model[y]) > half_size):
                angle = (angle + 180) % 360
            angle += expovariate(lambd) - degrees
            theta = radians(angle)
            dy = magnitude * sin(theta)
            dx = magnitude * cos(theta)
            turtle_model[x] += dx
            turtle_model[y] += dy
            turtle_model[x + 2] = angle


pyglet.clock.schedule_interval(update, 1/30)

pyglet.app.run()

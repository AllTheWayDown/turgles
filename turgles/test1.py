from __future__ import division, print_function, absolute_import

from random import randint, random, expovariate

from math import radians, sin, cos, pi
from time import time
import pyglet
from ctypes import sizeof

from array import array

from turgles.renderer import BaseRenderer
from turgles.gles20 import *
from turgles.shader import *
from turgles.util import measure

from turgles.config import *

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

turtle_model = array('f', list(gen_world()))


print(turtle_model[0:8])


class Renderer(BaseRenderer):
    """Uses single instanced drawing, with custom math and storage"""
    vertex_shader = 'shaders/turtles1.vert'
    fragment_shader = 'shaders/turtles.frag'

    def setup_program(self):
        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.turtle_attr1 = glGetAttribLocation(self.program.id, b"turtle1")
        self.turtle_attr2 = glGetAttribLocation(self.program.id, b"turtle2")

        self.program.bind()
        self.program.uniforms['scale'].set(self.half_width, self.half_height)

        # vertex buffer
        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(self.geometry.vertices)
        self.vertex_buffer.set(self.vertex_attr)

        # index buffer
        self.index_buffer = Buffer(
            GL_ELEMENT_ARRAY_BUFFER, GLushort, GL_STATIC_DRAW
        )
        self.index_buffer.load(self.geometry.indices)
        self.index_buffer.bind()

        # model buffer
        self.turtle_buffer = VertexBuffer(GLfloat, GL_DYNAMIC_DRAW)

    def render(self, turtle_data, count=None):
        if count is None:
            count = num_turtles
        self.window.clear()

        with measure("load"):
            self.turtle_buffer.load(turtle_data)

        with measure("render"):
            self.turtle_buffer.set(
                self.turtle_attr1, stride=32, offset=0, divisor=1)
            self.turtle_buffer.set(
                self.turtle_attr2, stride=32, offset=16, divisor=1)
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.geometry.indices_length,
                GL_UNSIGNED_SHORT,
                0,
                count,
            )

renderer = Renderer(world_size, world_size, shape)

@renderer.window.event
def on_draw():
    renderer.render(turtle_model)

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
            angle += expovariate(lambd) - degrees
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


pyglet.clock.schedule_interval(update, 1/30)
pyglet.app.run()

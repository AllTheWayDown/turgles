from __future__ import division, print_function, absolute_import

from random import randint, random, expovariate

from math import radians, sin, cos, pi
from time import time
import pyglet
from ctypes import sizeof

from array import array

from renderer import BaseRenderer
from gles20 import *
from shader import *
from util import measure

from config import *

# world coords
turtle_data_size = 4
def gen_world():
    for i in range(num_turtles):
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield random() * 360.0
        yield turtle_size  # * random() + 1.0

turtle_model = array('f', list(gen_world()))

class Renderer(BaseRenderer):
    """Uses single instanced drawing, with custom math and storage"""
    vertex_shader = 'shaders/turtles1.vert'
    fragment_shader = 'shaders/turtles.frag'

    def setup_program(self):
        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.turtle_attr = glGetAttribLocation(self.program.id, b"turtle")

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
        #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer.id)
        ##self.index_buffer.bind(self.vertex_attr, size=2)

        # model buffer
        self.turtle_buffer = VertexBuffer(GLfloat, GL_DYNAMIC_DRAW)

    def render(self, turtle_data):
        self.window.clear()

        with measure("load"):
            self.turtle_buffer.load(turtle_data)

        with measure("render"):
            self.turtle_buffer.set(self.turtle_attr, divisor=1)
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.geometry.indices_length,
                GL_UNSIGNED_SHORT,
                0,
                len(turtle_data) // turtle_data_size
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

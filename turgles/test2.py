from __future__ import division, print_function, absolute_import

from random import randint, random, expovariate

from math import radians, sin, cos, pi
from time import time
import pyglet
from ctypes import sizeof
from gles20 import *
from shader import *
from array import array

from renderer import BaseRenderer
from util import measure

from config import *

def gen_world():
    for i in range(num_turtles):
        angle = random() * 360.0
        theta = radians(angle)
        yield [
            random() * world_size - half_size,
            random() * world_size - half_size,
            cos(theta),
            sin(theta),
            turtle_size,
            turtle_size,
            angle,
        ]

turtle_model = list(gen_world())


class Renderer(BaseRenderer):
    """uses uniforms and custom maths"""
    vertex_shader = 'shaders/turtles2.vert'
    fragment_shader = 'shaders/turtles.frag'

    def setup_program(self):
        self.program.bind()

        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")

        self.program.uniforms['scale'].set(self.half_width, self.half_height)

        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(self.geometry.vertices)
        self.vertex_buffer.set(self.vertex_attr)
        self.index_buffer = Buffer(
            GL_ELEMENT_ARRAY_BUFFER, GLushort, GL_STATIC_DRAW
        )
        self.index_buffer.load(self.geometry.indices)
        self.index_buffer.bind()


    def render(self, turtle_data):
        self.window.clear()
        u_pos = self.program.uniforms['turtle']
        u_size = self.program.uniforms['size']

        with measure("render"):
            for data in turtle_data:
                with measure("load"):
                    u_pos.set(data[0], data[1], data[2], data[3])
                    u_size.set(data[4], data[5])
                glDrawElements(
                    GL_TRIANGLES,
                    self.geometry.indices_length,
                    GL_UNSIGNED_SHORT,
                    0
                )

renderer = Renderer(world_size, world_size, shape)

@renderer.window.event
def on_draw():
    renderer.render(turtle_model)

def update(dt):
    X = 0
    Y = 1
    CT = 2
    ST = 3
    SX = 4
    SY = 5
    ANGLE = 6
    with measure("update"):
        magnitude = speed * dt
        for t in turtle_model:
            angle = t[ANGLE]
            if (abs(t[X]) > half_size or abs(t[Y]) > half_size):
                angle = angle % 360
            angle += expovariate(lambd) - degrees
            theta = radians(angle)
            ct = cos(theta)
            st = sin(theta)
            t[X] += magnitude * ct
            t[Y] += magnitude * st
            t[CT] = ct
            t[ST] = st
            t[ANGLE] = angle


pyglet.clock.schedule_interval(update, 1/30)

pyglet.app.run()

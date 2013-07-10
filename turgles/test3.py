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
from transformations import (
    translation_matrix,
    rotation_matrix,
    scale_matrix,
    concatenate_matrices,
    compose_matrix,
)

from config import *

# world coords
turtle_data_size = 16  # 4x4 matrix

turtle_objects = []
turtle_model = array('f', [0] * num_turtles * 16)



def gen_world():
    for i in range(num_turtles):
        size = turtle_size
        scalex = scaley = 1 / half_size * size
        degrees = random() * 360.0
        angle = radians(degrees)

        x = random() * world_size - half_size
        y = random() * world_size - half_size
        obj = [x, y, degrees, size]
        turtle_objects.append(obj)
        M = compose_matrix(
            scale=[scalex, scaley, 0],
            translate=[x/half_size, y/half_size, 0],
            angles=[0, 0, angle],
        )
        for k, column in enumerate(M):
            for j, row in enumerate(column):
                print(i * 64 + (k * 4) + j)
                turtle_model[(i * 16) + (k * 4) + j] = row

gen_world()

class Renderer(BaseRenderer):
    """Uses single instanced drawing, with custom math and storage"""
    vertex_shader = 'shaders/turtles3.vert'
    fragment_shader = 'shaders/turtles.frag'

    def setup_program(self):
        #glClearColor(1.0, 1.0, 1.0, 0.0)
        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.turtle_attr = glGetAttribLocation(self.program.id, b"turtle")

        self.program.bind()

        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(self.geometry.vertices)
        self.vertex_buffer.set(self.vertex_attr)
        self.index_buffer = Buffer(
            GL_ELEMENT_ARRAY_BUFFER, GLushort, GL_STATIC_DRAW
        )
        self.index_buffer.load(self.geometry.indices)
        self.index_buffer.bind()

        self.turtle_buffer = VertexBuffer(GLfloat, GL_DYNAMIC_DRAW)

    def render(self, turtle_data):
        self.window.clear()

        with measure("load"):
            self.turtle_buffer.load(turtle_data)

        a, b, c, d = [self.turtle_attr + i for i in range(4)]
        with measure("render"):
            self.turtle_buffer.set(a, stride=64, offset=0, divisor=1)
            self.turtle_buffer.set(b, stride=64, offset=16, divisor=1)
            self.turtle_buffer.set(c, stride=64, offset=32, divisor=1)
            self.turtle_buffer.set(d, stride=64, offset=48, divisor=1)
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.geometry.indices_length,
                GL_UNSIGNED_SHORT,
                0, #, self.geometry.indices_pointer,
                len(turtle_data) // turtle_data_size
            )

renderer = Renderer(world_size, world_size, shape)

@renderer.window.event
def on_draw():
    renderer.render(turtle_model)

MEM = memoryview(turtle_model)
def update(dt):
    with measure("update"):
        magnitude = speed * dt
        for i, obj in enumerate(turtle_objects):
            offset = i * 16
            view = MEM[offset:offset+16]
            angle = obj[i + 2]
            #if (abs(turtle_model[x]) > half_size or
            #    abs(turtle_model[y]) > half_size):
            #    angle = (angle + 180) % 360
            angle += expovariate(lambd) - degrees
            theta = radians(angle)
            dy = magnitude * sin(theta)
            dx = magnitude * cos(theta)
            M = compose_matrix(
                translate=[dx/half_size, dy/half_size, 0],
                angles=[0, 0, theta]
            )
            obj[offset + 0] += dx
            obj[offset + 1] += dx
            obj[offset + 2] = angle
            view[:] = concatenate_matrices(M, view)


#pyglet.clock.schedule_interval(update, 1/30)
pyglet.app.run()

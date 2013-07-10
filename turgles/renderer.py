from __future__ import division, print_function, absolute_import

import pyglet

from turgles.gles20 import *  # NOQA

from turgles.shader import Program, Buffer

from turgles.geometry import TurtleGeometry
from turgles.util import measure
from turgles.shader import *
turtle_data_size = 8


class BaseRenderer(object):

    vertex_shader = None
    fragment_shader = None

    def __init__(self, width, height, shape='classic', samples=16,
            vertex_shader=None, fragment_shader=None):
        self.width = width
        self.half_width = width // 2
        self.height = height
        self.half_height = height // 2

        if vertex_shader is not None:
            self.vertex_shader = vertex_shader
        if fragment_shader is not None:
            self.fragment_shader = fragment_shader

        # constant shape for now
        self.geometry = TurtleGeometry.load_shape(shape)
        self.config = pyglet.gl.Config(
            double_buffer=True,
            sample_buffers=1,
            samples=samples,
            #major_version=3,
            #minor_version=1,
            #forward_compatible=True,
        )
        self.window = pyglet.window.Window(
            config=self.config,
            width=int(width),
            height=int(height)
        )

        self.load_program()
        self.setup_program()
        self.set_background_color()

    def set_background_color(self, color=None):
        if color is None:
            glClearColor(1.0, 1.0, 1.0, 0.0)
        else:
            glClearColor(color[0], color[1], color[2], 0.0)

    def load_program(self):
        self.program = Program(
            open(self.vertex_shader).read(),
            open(self.fragment_shader).read()
        )


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

    def render(self, turtle_data, count):
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
                count
            )



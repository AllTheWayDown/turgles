from __future__ import division, print_function, absolute_import

import pyglet

from turgles.gles20 import *  # NOQA

from turgles.shader import Program, Buffer

from turgles.geometry import TurtleGeometry
from turgles.util import measure
from turgles.shader import *

class BaseRenderer(object):

    vertex_shader = None
    fragment_shader = None

    def __init__(self, width, height, shape='classic', samples=None,
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
        kwargs = dict(double_buffer=True)
        if samples is not None:
            kwargs['sample_buffers'] = 1
            kwargs['samples'] = samples
            #major_version=3,
            #minor_version=1,
            #forward_compatible=True,
        self.config = pyglet.gl.Config(**kwargs)
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

        self.vao = GLuint()
        glGenVertexArrays(1, self.vao);
        glBindVertexArray(self.vao);

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
        self.turtle_buffer = VertexBuffer(GLfloat, GL_STREAM_DRAW)
        self.turtle_buffer.set(
            self.turtle_attr1, stride=32, offset=0, divisor=1)
        self.turtle_buffer.set(
            self.turtle_attr2, stride=32, offset=16, divisor=1)

    def render(self, turtle_data, num_turtles):
        self.window.clear()

        with measure("load"):
            self.turtle_buffer.load(turtle_data)

        with measure("draw"):
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.geometry.num_vertex,
                GL_UNSIGNED_SHORT,
                0,
                num_turtles
            )



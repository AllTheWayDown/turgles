from __future__ import division, print_function, absolute_import

import pyglet

from turgles.gles20 import *  # NOQA

from turgles.shader import Program

from turgles.geometry import SHAPES
from turgles.render.turtles import TurtleShapeVAO


class BaseRenderer(object):

    vertex_shader = None
    fragment_shader = None

    def __init__(
            self,
            width, height,
            samples=None,
            vertex_shader=None, fragment_shader=None):

        self.width = width
        self.half_width = width // 2
        self.height = height
        self.half_height = height // 2

        if vertex_shader is not None:
            self.vertex_shader = vertex_shader
        if fragment_shader is not None:
            self.fragment_shader = fragment_shader

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
        self.program.bind()
        self.program.uniforms['scale'].set(self.half_width, self.half_height)
        self.vao = {}
        for shape, geom in SHAPES.items():
            self.vao[shape] = TurtleShapeVAO(shape, self.program, geom)

    def render(self, *buffers):
        self.window.clear()
        for shape, data, size in buffers:
            vao = self.vao[shape]
            vao.render(data, size)

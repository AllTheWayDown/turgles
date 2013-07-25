from __future__ import division, print_function, absolute_import

import pyglet

from turgles.gl.api import glClearColor
from turgles.gl.program import Program
from turgles.render.turtles import TurtleShapeVAO
from turgles.geometry import SHAPES


class Renderer(object):

    vertex_shader = 'shaders/turtles1.vert'
    fragment_shader = 'shaders/turtles.frag'

    def __init__(
            self,
            width,
            height,
            samples=None):

        self.width = width
        self.half_width = width // 2
        self.height = height
        self.half_height = height // 2

        self.create_window(width, height, samples)
        self.set_background_color()
        self.compile_program()
        self.setup_vaos()

    def create_window(self, width, height, samples):
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

    def set_background_color(self, color=None):
        if color is None:
            glClearColor(1.0, 1.0, 1.0, 0.0)
        else:
            glClearColor(color[0], color[1], color[2], 0.0)

    def compile_program(self):
        self.program = Program(
            open(self.vertex_shader).read(),
            open(self.fragment_shader).read()
        )

    def setup_vaos(self):
        self.program.bind()
        self.program.uniforms['world_scale'].set(
            self.half_width, self.half_height)
        self.vao = {}
        for shape, geom in SHAPES.items():
            self.vao[shape] = TurtleShapeVAO(shape, self.program, geom)

    def render(self, buffers):
        self.window.clear()
        for shape, data, size in buffers:
            vao = self.vao[shape]
            vao.render(data, size)

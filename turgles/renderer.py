from __future__ import division, print_function, absolute_import

import pyglet

from turgles.gl.api import glClearColor
from turgles.gl.program import Program
from turgles.render.turtles import TurtleShapeVAO
from turgles.geometry import SHAPES
from turgles.buffer import TurtleBuffer


class Renderer(object):

    vertex_shader = 'shaders/turtles.vert'
    fragment_shader = 'shaders/turtles.frag'

    def __init__(
            self,
            width,
            height,
            samples=None,
            buffer_size=16):

        self.width = width
        self.half_width = width // 2
        self.height = height
        self.half_height = height // 2
        self.buffer_size = buffer_size

        self.create_window(width, height, samples)
        self.set_background_color()
        self.compile_program()
        self.setup_vaos()

        # per-shape buffers for turtle data
        self.buffers = {}

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

    def render(self):
        self.window.clear()
        for buffer in self.buffers.values():
            vao = self.vao[buffer.shape]
            vao.render(buffer.data, buffer.size)

    def create_turtle_data(self, shape):
        buffer = self.get_buffer(shape)
        try:
            return buffer.new()
        except TurtleBuffer.Full:
            raise

    def get_buffer(self, shape):
        if shape in self.buffers:
            return self.buffers[shape]

        buffer = TurtleBuffer(shape, self.buffer_size)
        self.buffers[shape] = buffer
        return buffer

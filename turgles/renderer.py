from __future__ import division, print_function, absolute_import

import pyglet

import pkg_resources

from turgles.buffer import BufferManager
from turgles.geometry import SHAPES
from turgles.gl.api import glClearColor
from turgles.gl.program import Program
from turgles.render.turtles import TurtleShapeVAO


class Renderer(object):

    vertex_shader = pkg_resources.resource_string(
        'turgles', 'shaders/turtles.vert').decode('utf8')
    fragment_shader = pkg_resources.resource_string(
        'turgles', 'shaders/turtles.frag').decode('utf8')

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

        self.create_window(width, height, samples)
        self.set_background_color()
        self.compile_program()
        self.setup_vaos()

        self.manager = BufferManager(buffer_size)

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
        self.program = Program(self.vertex_shader, self.fragment_shader)

    def setup_vaos(self):
        self.program.bind()
        self.program.uniforms['world_scale'].set(
            self.half_width, self.half_height)
        self.vao = {}
        for shape, geom in SHAPES.items():
            self.vao[shape] = TurtleShapeVAO(shape, self.program, geom)

    # ninjaturtle interface
    def render(self, flip=True):
        self.window.clear()
        for buffer in self.manager.buffers.values():
            vao = self.vao[buffer.shape]
            vao.render(buffer.data, buffer.count)
        if flip:
            self.window.flip()

    # ninjaturtle interface
    def create_turtle_data(self, shape, init=None):
        return self.manager.create_turtle(shape, init)

    # ninjaturtle interface
    def destroy_turtle_data(self, id):
        self.manager.destroy_turtle(id)

    # ninjaturtle interface
    def set_shape(self, id, shape):
        self.manager.set_shape(id, shape)

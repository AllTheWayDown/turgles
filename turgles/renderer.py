from __future__ import division, print_function, absolute_import

import pyglet

from gles20 import *  # NOQA

from shader import Program, Buffer

from geometry import TurtleGeometry
from util import measure

turtle_data_size = 7


class BaseRenderer(object):

    vertex_shader = None
    fragment_shader = None

    def __init__(self, width, height, shape='classic', samples=16):
        self.width = width
        self.half_width = width // 2
        self.height = height
        self.half_height = height // 2

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

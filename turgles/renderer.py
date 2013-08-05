from __future__ import division, print_function, absolute_import
from math import tan, radians

import pkg_resources

import pyglet
from pyglet.window import key

from turgles.buffer import BufferManager
from turgles.geometry import SHAPES
from turgles.gl.api import (
    glClearColor,
    glDepthFunc,
    glDepthMask,
    glDepthRangef,
    GLsizei,
    GL_DEPTH_TEST,
    glEnable,
    GL_LEQUAL,
    GL_TRUE,
    glViewport,
)
from turgles.gl.program import Program
from turgles.render.turtles import TurtleShapeVAO


def identity():
    return [1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1]


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

        self.perspective_matrix = identity()
        self.set_perspective()
        self.view_matrix = identity()
        self.view_matrix[12] = 0.0
        self.view_matrix[13] = 0.0
        self.view_matrix[14] = 0.0
        self.set_view()

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
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LEQUAL)
        glDepthRangef(0.0, 1.0)

        self.speed = 1

        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)

        pyglet.clock.schedule_interval(self.move_camera, 1/30)

        @self.window.event
        def on_resize(width, height):
            self.width = width
            self.height = height
            self.set_perspective()
            return pyglet.event.EVENT_HANDLED

    def move_camera(self, dt):
        if self.keys[key.UP]:
            self.view_matrix[13] -= self.speed * dt
        elif self.keys[key.DOWN]:
            self.view_matrix[13] += self.speed * dt

        if self.keys[key.LEFT]:
            self.view_matrix[12] += self.speed * dt
        elif self.keys[key.RIGHT]:
            self.view_matrix[12] -= self.speed * dt

        if self.keys[key.PAGEUP]:
            self.view_matrix[14] += self.speed * dt
        elif self.keys[key.PAGEDOWN]:
            self.view_matrix[14] -= self.speed * dt

        self.set_view()

    def set_perspective(self, near=0, far=2.0, fov=45.0):
        scale = 1.0 / tan(radians(fov) / 2.0)
        diff = near - far
        scale = 1.0
        self.perspective_matrix[0] = scale / (self.width / self.height)
        self.perspective_matrix[5] = scale
        self.perspective_matrix[10] = (far + near) / diff
        self.perspective_matrix[11] = -1.0
        self.perspective_matrix[14] = (2 * far * near) / diff
        self.program.bind()
        self.program.uniforms['projection'].set_matrix(
            self.perspective_matrix)
        scale = min(self.width, self.height) // 2
        self.program.uniforms['world_scale'].set(scale)
        self.program.unbind()
        glViewport(
            0, 0,
            (GLsizei)(int(self.width)),
            (GLsizei)(int(self.height))
        )

    def set_view(self):
        self.program.bind()
        self.program.uniforms['view'].set_matrix(
            self.view_matrix)
        self.program.unbind()

    def set_background_color(self, color=None):
        if color is None:
            glClearColor(1.0, 1.0, 1.0, 0.0)
        else:
            glClearColor(color[0], color[1], color[2], 0.0)

    def compile_program(self):
        self.program = Program(self.vertex_shader, self.fragment_shader)

    def setup_vaos(self):
        self.program.bind()
        self.vao = {}
        for shape, geom in SHAPES.items():
            self.vao[shape] = TurtleShapeVAO(shape, self.program, geom)

    # ninjaturtle engine interface
    def render(self, flip=True):
        self.window.clear()
        for buffer in self.manager.buffers.values():
            if buffer.count > 0:
                vao = self.vao[buffer.shape]
                vao.render(buffer.data, buffer.count)
        if flip:
            self.window.flip()

    # ninjaturtle engine interface
    def create_turtle_data(self, shape, init=None):
        return self.manager.create_turtle(shape, init)

    # ninjaturtle engine interface
    def destroy_turtle_data(self, id):
        self.manager.destroy_turtle(id)

    # ninjaturtle engine interface
    def set_shape(self, id, shape):
        return self.manager.set_shape(id, shape)

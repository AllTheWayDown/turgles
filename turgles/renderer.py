from __future__ import division, print_function, absolute_import
from math import tan, radians

import pkg_resources

import pyglet
from pyglet.window import key

from turgles.buffer import BufferManager
from turgles.memory import TURTLE_MODEL_DATA_SIZE, TURTLE_COLOR_DATA_SIZE
from turgles.geometry import SHAPES
from turgles.turgle import Turgle
from turgles.gl.api import (
    glClearColor,
    glGetIntegerv,
    GLsizei,
    GL_DEPTH_TEST,
    glEnable,
    GL_LEQUAL,
    GL_TRUE,
    glViewport,
    GLint,
    GL_MAX_SAMPLES,
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
        max_samples = GLint()
        glGetIntegerv(GL_MAX_SAMPLES, max_samples)
        if max_samples.value > 0:
            kwargs['sample_buffers'] = 1
            kwargs['samples'] = min(max_samples.value, 16)
            print("Setting antialiasing to %s" % kwargs['samples'])
        self.config = pyglet.gl.Config(**kwargs)
        self.window = pyglet.window.Window(
            config=self.config,
            width=int(width),
            height=int(height)
        )
        glEnable(GL_DEPTH_TEST)

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

    def set_perspective(self, near=0, far=3, fov=90.0):
        scale = 1.0 / tan(radians(fov) / 2.0)
        self.perspective_matrix[0] = scale / (self.width / self.height)
        self.perspective_matrix[5] = scale
        self.perspective_matrix[10] = -(far + near) / (far - near)
        self.perspective_matrix[11] = -1.0
        self.perspective_matrix[14] = (-2 * far * near) / (far - near)
        # ortho, doesn't work
        #self.perspective_matrix[0] = 2.0/self.width
        #self.perspective_matrix[5] = 2.0/self.height
        #self.perspective_matrix[10] = 1.0/(far - near)
        #self.perspective_matrix[14] = -near/(far - near)
        #self.perspective_matrix[15] = 1.0
        self.program.bind()
        self.program.uniforms['projection'].set(
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
        self.program.uniforms['view'].set(
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
                vao.render(buffer.model, buffer.color, buffer.count)
        if flip:
            self.window.flip()

    # ninjaturtle engine interface
    def create_turtle(self, model, init, shape='classic'):
        model_init = init[:TURTLE_MODEL_DATA_SIZE]
        color_init = init[TURTLE_MODEL_DATA_SIZE:]
        assert len(color_init) == TURTLE_COLOR_DATA_SIZE
        data, color = self.manager.create_turtle(
            model.id, shape, model_init, color_init)
        model.data = data
        model.backend = Turgle(self, model, color, shape)

    # ninjaturtle engine interface
    def destroy_turtle_data(self, id):
        self.manager.destroy_turtle(id)

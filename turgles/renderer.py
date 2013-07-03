import pyglet

from gles20 import *  # NOQA

from shader import Program, Buffer

from geometry import TurtleGeometry

turtle_data_size = 4


class TurGLESRenderer(object):

    def __init__(self, width, height):
        self.width = width
        self.half_width = width // 2
        self.height = height
        self.half_height = height // 2
        self.geometry = TurtleGeometry.load_shape('turtle')

        self.window = pyglet.window.Window(
            width=int(width), height=int(height))

        self.program = Program(
            open('shaders/turtles.vert').read(),
            open('shaders/turtles.frag').read()
        )

        glClearColor(1.0, 1.0, 1.0, 0.0)

        self.vertex_attr = glGetAttribLocation(self.program.id, b"shape_vertex")
        self.turtle_attr = glGetAttribLocation(self.program.id, b"turtle")

        self.program.bind()
        self.program.uniforms['scale'].set(self.half_width, self.half_height)

        self.vertex_buffer = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STATIC_DRAW)
        self.vertex_buffer.load(self.geometry.vertices)
        self.vertex_buffer.bind(self.vertex_attr, size=2)

        self.turtle_buffer = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STREAM_READ)

    def render(self, turtle_data):
        self.window.clear()
        self.turtle_buffer.load(turtle_data)
        self.turtle_buffer.bind(self.turtle_attr, size=4, divisor=1)
        glDrawElementsInstanced(
            GL_TRIANGLES,
            self.geometry.indices_length,
            GL_UNSIGNED_SHORT,
            self.geometry.indices_pointer,
            len(turtle_data) // 4
        )


from __future__ import division, print_function, absolute_import

from turgles.gl.api import (
    GL_ELEMENT_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    GL_STREAM_DRAW,
    GL_TRIANGLES,
    GL_UNSIGNED_SHORT,
    GLuint,
    GLushort,
    GLfloat,
    glGetAttribLocation,
    glGenVertexArrays,
    glBindVertexArray,
    glDrawElementsInstanced,
)

from turgles.gl.buffer import VertexBuffer, Buffer
from turgles.util import measure


class TurtleShapeVAO(object):
    """A VAO for rendering mutliple versions of a specific turtle shape.

    Creates VAO/vertex/index/model arrays, and can render them given turtle
    data."""

    def __init__(self, name, program, geometry):
        self.name = name
        self.program = program
        self.geometry = geometry
        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.turtle_attr1 = glGetAttribLocation(self.program.id, b"turtle1")
        self.turtle_attr2 = glGetAttribLocation(self.program.id, b"turtle2")

        # create VAO to store Vertex attribute state for later
        self.vao = GLuint()
        glGenVertexArrays(1, self.vao)

        # bind VAO to record array setup/state
        glBindVertexArray(self.vao)

        # load/bind/configure vertex buffer
        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(geometry.vertices)
        self.vertex_buffer.set(self.vertex_attr)

        # load/bind index buffer
        self.index_buffer = Buffer(
            GL_ELEMENT_ARRAY_BUFFER, GLushort, GL_STATIC_DRAW
        )
        self.index_buffer.load(geometry.indices)
        self.index_buffer.bind()

        # turtle model buffer
        self.turtle_buffer = VertexBuffer(GLfloat, GL_STREAM_DRAW)
        self.turtle_buffer.set(
            self.turtle_attr1, stride=32, offset=0, divisor=1)
        self.turtle_buffer.set(
            self.turtle_attr2, stride=32, offset=16, divisor=1)

        # VAO now configured, so unbind
        glBindVertexArray(0)

    def render(self, turtle_data, num_turtles):
        self.program.bind()
        glBindVertexArray(self.vao)

        with measure("load {}".format(self.name)):
            self.turtle_buffer.load(turtle_data)
            self.program.uniforms['geometry_scale'].set(self.geometry.scale)

        with measure("draw {}".format(self.name)):
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.geometry.num_vertex,
                GL_UNSIGNED_SHORT,
                0,
                num_turtles
            )

        glBindVertexArray(0)
        self.program.unbind()

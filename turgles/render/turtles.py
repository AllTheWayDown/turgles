from __future__ import division, print_function, absolute_import

from turgles.gl.api import (
    GL_STATIC_DRAW,
    GL_STREAM_DRAW,
    GL_TRIANGLES,
    GLuint,
    GLfloat,
    glGetAttribLocation,
    glGenVertexArrays,
    glBindVertexArray,
    glDrawArraysInstanced,
)

from turgles.gl.buffer import VertexBuffer
from turgles.memory import TURTLE_MODEL_DATA_SIZE, TURTLE_COLOR_DATA_SIZE


class TurtleShapeVAO(object):
    """A VAO for rendering mutliple versions of a specific turtle shape.

    Creates VAO/vertex/index/model arrays, and can render them given turtle
    data."""

    def __init__(self, name, program, geometry):
        self.name = name
        self.program = program
        self.geometry = geometry

        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.edge_attr = glGetAttribLocation(self.program.id, b"edge")

        self.model_attr = glGetAttribLocation(self.program.id, b"turtle_model")
        self.color_attr = glGetAttribLocation(self.program.id, b"turtle_color")

        # create VAO to store Vertex attribute state for later
        self.vao = GLuint()
        glGenVertexArrays(1, self.vao)

        # bind VAO to record array setup/state
        glBindVertexArray(self.vao)

        # load shape data into vertex buffer
        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(geometry.edges)
        self.vertex_buffer.partition(
            [(self.vertex_attr, 4), (self.edge_attr, 3)]
        )

        # allocate/configure instanced buffers
        # turtle model buffer
        self.model_buffer = VertexBuffer(GLfloat, GL_STREAM_DRAW)
        # mat4 is 4 sequential locations
        array = [
            (self.model_attr,     4),
            (self.model_attr + 1, 4),
            (self.model_attr + 2, 4),
            (self.model_attr + 3, 4),
        ]
        self.model_buffer.partition(array, divisor=1)
        # turtle color buffer
        self.color_buffer = VertexBuffer(GLfloat, GL_STREAM_DRAW)
        # mat3 is 3 sequential locations
        array = [
            (self.color_attr,     3),
            (self.color_attr + 1, 3),
            (self.color_attr + 2, 3),
        ]
        self.color_buffer.partition(array, divisor=1)

        # VAO now configured, so unbind
        glBindVertexArray(0)

    def render(self, model, color, num_turtles):
        """Renders all turtles of a given shape"""
        self.program.bind()
        glBindVertexArray(self.vao)

        self.model_buffer.load(model.data, model.byte_size)
        self.color_buffer.load(color.data, color.byte_size)

        glDrawArraysInstanced(
            GL_TRIANGLES,
            0,
            len(self.geometry.edges) // 7,  # 7 = 4 for vertex, 3 for edge
            num_turtles
        )

        glBindVertexArray(0)
        self.program.unbind()

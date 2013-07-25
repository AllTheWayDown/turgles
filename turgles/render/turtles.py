from __future__ import division, print_function, absolute_import

from turgles import gl

from shader import VertexBuffer, Buffer

from turgles.util import measure


class TurtleShapeVAO(object):
    """A VAO for rendering mutliple versions of a specific turtle shape.

    Creates VAO/vertex/index/model arrays, and can render them given turtle
    data."""

    def __init__(self, name, program, geometry):
        self.name = name
        self.program = program
        self.geometry = geometry
        self.vertex_attr = gl.GetAttribLocation(self.program.id, b"vertex")
        self.turtle_attr1 = gl.GetAttribLocation(self.program.id, b"turtle1")
        self.turtle_attr2 = gl.GetAttribLocation(self.program.id, b"turtle2")

        # create VAO to store Vertex attribute state for later
        self.vao = gl.GLuint()
        gl.GenVertexArrays(1, self.vao)

        # bind VAO to record array setup/state
        gl.BindVertexArray(self.vao)

        # load/bind/configure vertex buffer
        self.vertex_buffer = VertexBuffer(gl.GLfloat, gl.GL_STATIC_DRAW)
        self.vertex_buffer.load(geometry.vertices)
        self.vertex_buffer.set(self.vertex_attr)

        # load/bind index buffer
        self.index_buffer = Buffer(
            gl.GL_ELEMENT_ARRAY_BUFFER, gl.GLushort, gl.GL_STATIC_DRAW
        )
        self.index_buffer.load(geometry.indices)
        self.index_buffer.bind()

        # turtle model buffer
        self.turtle_buffer = VertexBuffer(gl.GLfloat, gl.GL_STREAM_DRAW)
        self.turtle_buffer.set(
            self.turtle_attr1, stride=32, offset=0, divisor=1)
        self.turtle_buffer.set(
            self.turtle_attr2, stride=32, offset=16, divisor=1)

        # VAO now configured, so unbind
        gl.BindVertexArray(0)

    def render(self, turtle_data, num_turtles):
        self.program.bind()
        gl.BindVertexArray(self.vao)

        with measure("load {}".format(self.name)):
            self.turtle_buffer.load(turtle_data)

        with measure("draw {}".format(self.name)):
            gl.DrawElementsInstanced(
                gl.GL_TRIANGLES,
                self.geometry.num_vertex,
                gl.GL_UNSIGNED_SHORT,
                0,
                num_turtles
            )

        gl.BindVertexArray(0)
        self.program.unbind()

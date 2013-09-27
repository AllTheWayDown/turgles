from __future__ import division, print_function, absolute_import

import pkg_resources


from turgles.geometry import SHAPES
from turgles.gl.api import (
    GL_ELEMENT_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    GL_UNSIGNED_SHORT,
    GLuint,
    GLushort,
    GLfloat,
    glGetAttribLocation,
    glGenVertexArrays,
    glBindVertexArray,
    glDrawElements,
)
from turgles.renderer import Renderer
from turgles.gl.buffer import VertexBuffer, Buffer
from turgles.memory import TURTLE_DATA_SIZE
from turgles.util import measure


class ESTurtleShapeVAO(object):
    """A VAO for rendering mutliple versions of a specific turtle shape.

    Creates VAO/vertex/index/model arrays, and can render them given turtle
    data."""

    def __init__(self, name, program, geometry):
        self.name = name
        self.program = program
        self.geometry = geometry

        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")

        # TODO: remove use of vao's, as not in ES2!
        # create VAO to store Vertex attribute state for later
        self.vao = GLuint()
        glGenVertexArrays(1, self.vao)

        # bind VAO to record array setup/state
        glBindVertexArray(self.vao)

        # load/bind/configure vertex buffer
        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(geometry.vertices)
        self.vertex_buffer.set(self.vertex_attr, 4)

        # load/bind index buffer
        self.index_buffer = Buffer(
            GL_ELEMENT_ARRAY_BUFFER, GLushort, GL_STATIC_DRAW
        )
        self.index_buffer.load(geometry.indices)
        self.index_buffer.bind()

        # VAO now configured, so unbind
        glBindVertexArray(0)

    def render(self, turtle_data, num_turtles):
        self.program.bind()
        glBindVertexArray(self.vao)

        a = self.program.uniforms['turtle1']
        b = self.program.uniforms['turtle2']
        c = self.program.uniforms['turtle_fill_color']

        with measure("loop"):
            for i in range(0, len(turtle_data), TURTLE_DATA_SIZE):
                with measure('load'):
                    a.set(*tuple(turtle_data[i:i+4]))
                    b.set(*tuple(turtle_data[i+4:i+8]))
                    c.set(*tuple(turtle_data[i+8:i+12]))

                with measure('draw'):
                    glDrawElements(
                        GL_TRIANGLES,
                        self.geometry.num_vertex,
                        GL_UNSIGNED_SHORT,
                        0,
                    )

        glBindVertexArray(0)
        self.program.unbind()


class ES2Renderer(Renderer):

    vertex_shader = pkg_resources.resource_string(
        'turgles', 'shaders/turtles_es.vert').decode('utf8')
    fragment_shader = pkg_resources.resource_string(
        'turgles', 'shaders/turtles_es.frag').decode('utf8')

    def setup_vaos(self):
        self.program.bind()
        self.vao = {}
        for shape, geom in SHAPES.items():
            self.vao[shape] = ESTurtleShapeVAO(shape, self.program, geom)

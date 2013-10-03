from __future__ import division, print_function, absolute_import

import pkg_resources


from turgles.geometry import SHAPES
from turgles.gl.api import (
    GL_ELEMENT_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    GL_UNSIGNED_SHORT,
    GLushort,
    GLfloat,
    glGetAttribLocation,
    glDrawArrays,
    glGetProgramiv, GLint,
    GL_ACTIVE_ATTRIBUTES,
)
from turgles.renderer import Renderer
from turgles.gl.buffer import VertexBuffer, Buffer
from turgles.memory import TURTLE_DATA_SIZE
from turgles.util import measure


class ESTurtleShapeRenderer(object):
    """A Renderer for rendering mutliple versions of a specific turtle shape.

    Creates vertex/index/model arrays, and can render them given turtle
    data."""

    def __init__(self, name, program, geometry):
        self.name = name
        self.program = program
        self.geometry = geometry

        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.edge_attr = glGetAttribLocation(self.program.id, b"edge")
        count = GLint(0)
        glGetProgramiv(self.program.id, GL_ACTIVE_ATTRIBUTES, count)

        # load/bind/configure vertex buffer
        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.vertex_buffer.load(geometry.edges)
        self.vertex_buffer.partition(
            [(self.vertex_attr, 4), (self.edge_attr, 3)]
        )

        # load/bind index buffer
        #self.index_buffer = Buffer(
        #    GL_ELEMENT_ARRAY_BUFFER, GLushort, GL_STATIC_DRAW
        #)
        #self.index_buffer.load(geometry.indices)
        #self.index_buffer.bind()

    def render(self, turtle_data, num_turtles):
        self.program.bind()

        # no VAOs so have to set manually
        self.vertex_buffer.partition(
            [(self.vertex_attr, 4), (self.edge_attr, 3)]
        )
        #self.index_buffer.bind()

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
                    glDrawArrays(
                        GL_TRIANGLES,
                        0,
                        len(self.geometry.edges) // 7,
                    )

        self.vertex_buffer.unbind()
        #self.index_buffer.unbind()
        self.program.unbind()


class ES2Renderer(Renderer):

    vertex_shader = pkg_resources.resource_string(
        'turgles', 'shaders/turtles_es.vert').decode('utf8')
    fragment_shader = pkg_resources.resource_string(
        'turgles', 'shaders/turtles.frag').decode('utf8')

    def setup_vaos(self):
        self.program.bind()
        self.vao = {}
        for shape, geom in SHAPES.items():
            self.vao[shape] = ESTurtleShapeRenderer(shape, self.program, geom)

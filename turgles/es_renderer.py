from __future__ import division, print_function, absolute_import

import pkg_resources


from turgles.geometry import SHAPES
from turgles.gl.api import (
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    GLfloat,
    glGetAttribLocation,
    glDrawArrays,
)
from turgles.renderer import Renderer
from turgles.gl.buffer import VertexBuffer
from turgles.util import measure
from turgles import memory

BATCH_SIZE = 145  # see shader


class ESTurtleShapeRenderer(object):
    """A Renderer for rendering mutliple versions of a specific turtle shape.

    Creates vertex/index/model arrays, and can render them given turtle
    data."""

    def __init__(self, name, program, geometry):
        self.name = name
        self.program = program
        self.geometry = geometry
        # size of batched draw calls
        self.batch = BATCH_SIZE

        self.vertex_attr = glGetAttribLocation(self.program.id, b"vertex")
        self.edge_attr = glGetAttribLocation(self.program.id, b"edge")
        self.index_attr = glGetAttribLocation(self.program.id, b"index")

        # load/bind/configure vertex buffer
        self.vertex_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        batched_edges = list(geometry.edges) * self.batch
        self.vertex_buffer.load(memory.create_vertex_buffer(batched_edges))
        self.vertex_buffer.partition(
            [(self.vertex_attr, 4), (self.edge_attr, 3)]
        )

        uniform_indicies = []
        for i in range(self.batch):
            uniform_indicies.extend([i] * geometry.num_vertex)

        indices_buffer = memory.create_vertex_buffer(uniform_indicies)
        self.indices_buffer = VertexBuffer(GLfloat, GL_STATIC_DRAW)
        self.indices_buffer.load(indices_buffer)
        self.indices_buffer.set(self.index_attr, 1)

    def render(self, model, color, num_turtles):
        self.program.bind()

        # no VAOs so have to set manually
        self.vertex_buffer.partition(
            [(self.vertex_attr, 4), (self.edge_attr, 3)]
        )
        self.indices_buffer.set(self.index_attr, 1)

        model_uniform = self.program.uniforms['turtle_model_array[0]']
        color_uniform = self.program.uniforms['turtle_color_array[0]']

        model_iter = model.slice(self.batch)
        color_iter = color.slice(self.batch)

        with measure("loop"):
            for model_slice, color_slice in zip(model_iter, color_iter):
                # load batch of turtle data
                with measure('load'):
                    model_uniform.set(model_slice)
                    color_uniform.set(color_slice)

                with measure('draw'):
                    glDrawArrays(
                        GL_TRIANGLES,
                        0,
                        len(self.geometry.edges) // 7 * self.batch,
                    )

        self.vertex_buffer.unbind()
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

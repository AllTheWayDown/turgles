from turgles.gl.api import (
    GL_ARRAY_BUFFER,
    glBindBuffer,
    glBufferData,
    glEnableVertexAttribArray,
    GL_FALSE,
    glGenBuffers,
    GLuint,
    glVertexAttribDivisor,
    glVertexAttribPointer,
)

from turgles.memory import to_pointer, sizeof, TURTLE_DATA_SIZE
from turgles.gl.util import GL_TYPEMAP


class Buffer(object):
    """Generic buffer abstraction.

    Creation, binding and loading of GPU buffers.
    """

    def __init__(self, array_type, element_type, draw_type):
        self.array_type = array_type
        self.element_type = element_type
        self.element_flag, self.element_size = GL_TYPEMAP[element_type]
        self.draw_type = draw_type

        self.id = GLuint()
        glGenBuffers(1, self.id)

    def bind(self):
        glBindBuffer(self.array_type, self.id)

    def unbind(self):
        """Same for all buffer types"""
        glBindBuffer(self.array_type, 0)

    def load(self, data, n=None):
        """Data is cffi array"""
        self.bind()
        if n is None:
            # ffi's sizeof of understands arrays
            size = sizeof(data)
        else:
            size = 4 * TURTLE_DATA_SIZE * n
        glBufferData(
            self.array_type,
            size,
            to_pointer(data),
            self.draw_type)
        self.unbind()


class VertexBuffer(Buffer):
    """A VBO object to store vertex/model data.

    Specialisation of Buffer for attribute data, provides convient way to use
    glVertexAttribPointer, via set().
    """

    def __init__(self, element_type, draw_type):
        super(VertexBuffer, self).__init__(
            GL_ARRAY_BUFFER, element_type, draw_type)

    def set(self,
            index,
            interpolate=GL_FALSE,
            stride=0,
            offset=0,
            divisor=None):
        self.bind()
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(
            index,
            self.element_size,
            self.element_flag,
            interpolate,
            stride,
            offset
        )
        if divisor is not None:
            glVertexAttribDivisor(index, divisor)

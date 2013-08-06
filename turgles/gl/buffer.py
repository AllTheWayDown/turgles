from turgles.gl.api import (
    GL_ARRAY_BUFFER,
    glBindBuffer,
    glBufferData,
    glBufferSubData,
    glEnableVertexAttribArray,
    GL_FALSE,
    glGenBuffers,
    GLuint,
    glVertexAttribDivisor,
    glVertexAttribPointer,
)

from turgles.memory import to_pointer, sizeof
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

        # how much GPU memory have we added so far
        self.buffer_size = 0

        self.id = GLuint()
        glGenBuffers(1, self.id)

    def bind(self):
        glBindBuffer(self.array_type, self.id)

    def unbind(self):
        """Same for all buffer types"""
        glBindBuffer(self.array_type, 0)

    def load(self, data, size=None):
        """Data is cffi array"""
        self.bind()
        if size is None:
            # ffi's sizeof understands arrays
            size = sizeof(data)
        if size == self.buffer_size:
            # same size - no need to allocate new buffer, just copy
            glBufferSubData(
                self.array_type,
                0,
                size,
                to_pointer(data)
            )
        else:
            # buffer size has changed - need to allocate new buffer in the GPU
            glBufferData(
                self.array_type,
                size,
                to_pointer(data),
                self.draw_type
            )
            self.buffer_size = size
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
            size,
            interpolate=GL_FALSE,
            stride=0,
            offset=0,
            divisor=None):
        self.bind()
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(
            index,
            size,
            self.element_flag,
            interpolate,
            stride,
            offset
        )
        if divisor is not None:
            glVertexAttribDivisor(index, divisor)

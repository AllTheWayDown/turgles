from ctypes import sizeof
from pyglet.gl import *


class Buffer(object):

    def __init__(self, element_type, array_type, draw_type):
        self.element_type = element_type
        self.array_type = array_type
        self.draw_type = draw_type

        self.id = GLuint()
        glGenBuffers(1, self.id)

    def __enter__(self):
        self.bind()

    def __exit__(self, type, value, tb):
        self.unbind()

    def bind(self):
        glBindBuffer(self.array_type, self.id)

    def unbind(self):
        glBindBuffer(self.array_type, 0)

    def load(self, python_data):
        data = (self.element_type * len(python_data))(*python_data)
        self.bind()
        glBufferData(self.array_type, sizeof(data), data, self.draw_type)
        self.unbind()

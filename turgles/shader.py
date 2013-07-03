from array import array
from multiprocessing import Array
from ctypes import (
    byref,
    c_int,
    create_string_buffer,
    pointer,
    sizeof,
)
from gles20 import *  # NOQA

from util import (
    convert_to_cstring,
    get_program_log,
    get_shader_log,
    ShaderError,
)

class Uniform(object):
    """Represents a shader uniform"""

    UNIFORM_TYPES = {
        GL_FLOAT: (GLfloat, 1),
        GL_FLOAT_VEC2: (GLfloat, 2),
        GL_FLOAT_VEC3: (GLfloat, 3),
        GL_FLOAT_VEC4: (GLfloat, 4),
        GL_INT: (GLint, 1),
        GL_INT_VEC2: (GLint, 2),
        GL_INT_VEC3: (GLint, 3),
        GL_INT_VEC4: (GLint, 4),
        # TODO
        GL_BOOL: (GLboolean, 1),
        GL_BOOL_VEC2: (GLboolean, 2),
        GL_BOOL_VEC3: (GLboolean, 3),
        GL_BOOL_VEC4: (GLboolean, 4),
        GL_FLOAT_MAT2: (GLfloat, 2 * 2),
        GL_FLOAT_MAT3: (GLfloat, 3 * 3),
        GL_FLOAT_MAT4: (GLfloat, 4 * 4),
    }

    SETTERS = {
        GL_FLOAT: glUniform1f,
        GL_FLOAT_VEC2: glUniform2f,
        GL_FLOAT_VEC3: glUniform3f,
        GL_FLOAT_VEC4: glUniform4f,
        GL_INT: glUniform1i,
        GL_INT_VEC2: glUniform2i,
        GL_INT_VEC3: glUniform3i,
        GL_INT_VEC4: glUniform4i,
    }

    GETTERS = {
        GLfloat: glGetUniformfv,
        GLint: glGetUniformiv,
    }

    def __init__(self, program_id, index):
        self.program_id = program_id
        self.index = index
        self.size, self.type, self.cname = self.load_uniform(program_id, index)
        self.name = self.cname.decode('utf8')
        # unpack type constant
        self.item_type, self.length = self.UNIFORM_TYPES[self.type]
        # ctypes type to use
        self.ctype = self.item_type * self.length
        (GLfloat * 2)
        # setup correct gl functions to access
        self._getter = self.GETTERS[self.item_type]
        self._setter = self.SETTERS[self.type]

    @staticmethod
    def load_uniform(program_id, index):
        """Loads the meta data for one uniform"""
        n = 64  # max uniform length
        bufsize = GLsizei(n)
        length = pointer(GLsizei(0))
        size = pointer(GLint(0))
        type = pointer(GLenum(0))
        uname = create_string_buffer(n)
        glGetActiveUniform(
            program_id, index, bufsize, length, size, type, uname)
        return size[0], type[0], uname.value

    def __eq__(self, other):
        return self.index == other.index

    def get(self):
        params = self.ctype(*([0.0] * self.length))
        self._getter(self.program_id, self.index, params)
        return params

    def set(self, *data):
        if len(data) != self.length:
            raise ShaderError("Uniform '%s' is of length %d, not %d" %(
                self.name, self.length, len(data)))
        self._setter(self.index, *data)


class Buffer(object):

    TYPE_FLAGS = {
        GLfloat: GL_FLOAT,
        GLint: GL_INT,
        }

    ARRAY_TYPE_CODES  = {
        'f': GLfloat,
        'l': GLint,
    }

    def __init__(self, element_type, array_type, draw_type):
        self.element_type = element_type
        self.element_flag = self.TYPE_FLAGS[element_type]
        self.array_type = array_type
        self.draw_type = draw_type

        self.id = GLuint()
        glGenBuffers(1, self.id)

    def bind(self,
            index,
            size,
            interpolate=GL_FALSE,
            stride=0,
            offset=0,
            divisor=None):
        glBindBuffer(self.array_type, self.id)
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(
            index, size, self.element_flag, interpolate, stride, offset)
        if divisor is not None:
            glVertexAttribDivisor(index, divisor)

    def unbind(self):
        glBindBuffer(self.array_type, 0)

    def load(self, data):
        #assert self.ARRAY_TYPE_CODES[data.typecode] == self.element_type
        address, length = data.buffer_info()
        size = length * data.itemsize
        glBindBuffer(self.array_type, self.id)
        glBufferData(self.array_type, size, address, self.draw_type)
        glBindBuffer(self.array_type, 0)

class Program:
    """Shader program abstraction"""

    def __init__(self, vertex, fragment):
        self.id = glCreateProgram()
        self.create_shader(vertex, GL_VERTEX_SHADER)
        self.create_shader(fragment, GL_FRAGMENT_SHADER)
        self.compile()
        self.bind()

        self.uniforms = {}
        uniform_count = pointer(GLint(0))
        glGetProgramiv(self.id, GL_ACTIVE_UNIFORMS, uniform_count)
        for index in range(uniform_count[0]):
            uniform = Uniform(self.id, index)
            self.uniforms[uniform.name] = uniform

        self.unbind()

    def create_shader(self, src, type):
        shader_id = glCreateShader(type)
        glShaderSource(shader_id, 1, byref(convert_to_cstring(src)), None)
        glCompileShader(shader_id)

        status = c_int(0)
        glGetShaderiv(shader_id, GL_OBJECT_COMPILE_STATUS_ARB, byref(status))

        if not status:
            raise ShaderError(get_shader_log(shader_id))
        else:
            glAttachShader(self.id, shader_id)

    def compile(self):
        glLinkProgram(self.id)
        status = c_int(0)
        glGetProgramiv(self.id, GL_LINK_STATUS, byref(status))
        if not status:
            raise ShaderError(get_program_log(self.id))

    def bind(self):
        glUseProgram(self.id)

    def unbind(self):
        glUseProgram(0)

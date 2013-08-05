from ctypes import (
    pointer,
    create_string_buffer,
)

from turgles.gl.api import (
    GL_FALSE,
    GL_FLOAT,
    GL_FLOAT_VEC2,
    GL_FLOAT_VEC3,
    GL_FLOAT_VEC4,
    GL_INT,
    GL_INT_VEC2,
    GL_INT_VEC3,
    GL_INT_VEC4,
    GL_FLOAT_MAT2,
    GL_FLOAT_MAT3,
    GL_FLOAT_MAT4,
    GLint,
    GLsizei,
    GLenum,
    GLfloat,
    glUniform1f,
    glUniform2f,
    glUniform3f,
    glUniform4f,
    glUniform1i,
    glUniform2i,
    glUniform3i,
    glUniform4i,
    glUniformMatrix2fv,
    glUniformMatrix3fv,
    glUniformMatrix4fv,
    glGetUniformfv,
    glGetUniformiv,
    glGetActiveUniform,
    glGetActiveAttrib,
)


class UniformError(Exception):
    pass


def _load_variable(func, program_id, index):
    """Loads the meta data for a uniform or attribute"""
    n = 64  # max name length TODO: read from card
    bufsize = GLsizei(n)
    length = pointer(GLsizei(0))
    size = pointer(GLint(0))
    type = pointer(GLenum(0))
    uname = create_string_buffer(n)
    func(program_id, index, bufsize, length, size, type, uname)
    return size[0], type[0], uname.value.decode('utf8')


def load_uniform_data(program_id, index):
    return _load_variable(glGetActiveUniform, program_id, index)


def load_attribute_data(program_id, index):
    return _load_variable(glGetActiveAttrib, program_id, index)


class Uniform(object):
    """A shader uniform variable.

    Provides some convienices to set/get uniforms"""

    UNIFORM_TYPES = {
        GL_FLOAT: (GLfloat, 1),
        GL_FLOAT_VEC2: (GLfloat, 2),
        GL_FLOAT_VEC3: (GLfloat, 3),
        GL_FLOAT_VEC4: (GLfloat, 4),
        GL_INT: (GLint, 1),
        GL_INT_VEC2: (GLint, 2),
        GL_INT_VEC3: (GLint, 3),
        GL_INT_VEC4: (GLint, 4),
    }

    UNIFORM_MATRIX_TYPES = {
        GL_FLOAT_MAT2: (GLfloat, 4),
        GL_FLOAT_MAT3: (GLfloat, 9),
        GL_FLOAT_MAT4: (GLfloat, 16),
    }

    SETTERS = {
        # argument settings
        GL_FLOAT: glUniform1f,
        GL_FLOAT_VEC2: glUniform2f,
        GL_FLOAT_VEC3: glUniform3f,
        GL_FLOAT_VEC4: glUniform4f,
        GL_INT: glUniform1i,
        GL_INT_VEC2: glUniform2i,
        GL_INT_VEC3: glUniform3i,
        GL_INT_VEC4: glUniform4i,
        # v setters
        GL_FLOAT_MAT2: glUniformMatrix2fv,
        GL_FLOAT_MAT3: glUniformMatrix3fv,
        GL_FLOAT_MAT4: glUniformMatrix4fv,
    }

    GETTERS = {
        GLfloat: glGetUniformfv,
        GLint: glGetUniformiv,
    }

    def __init__(self, program_id, index):
        self.program_id = program_id
        self.index = index
        self.size, self.type, self.name = load_uniform_data(program_id, index)
        # unpack type constant
        if self.type in self.UNIFORM_TYPES:
            self.item_type, self.length = self.UNIFORM_TYPES[self.type]
            self.is_matrix = False
        else:
            self.item_type, self.length = self.UNIFORM_MATRIX_TYPES[self.type]
            self.is_matrix = True

        # ctypes type to use
        self.ctype = self.item_type * self.length
        # setup correct gl functions to access
        self._getter = self.GETTERS[self.item_type]
        self._setter = self.SETTERS[self.type]

    def __eq__(self, other):
        return self.index == other.index

    def get(self):
        params = self.ctype(*([0.0] * self.length))
        self._getter(self.program_id, self.index, params)
        return params

    def set(self, *data):
        assert not self.is_matrix, "set is only for non-matrix uniforms"
        if len(data) != self.length:
            raise UniformError("Uniform '%s' is of length %d, not %d" % (
                self.name, self.length, len(data)))
        self._setter(self.index, *data)

    def set_matrix(self, matrix):
        # data should be a cffi array
        assert self.is_matrix, "set_matrix only for matrix uniforms"
        if len(matrix) != self.length:
            raise UniformError("uniform '%s' is of length %d, not %d" % (
                self.name, self.length, len(matrix)))
        self._setter(self.index, 1, GL_FALSE, self.ctype(*matrix))

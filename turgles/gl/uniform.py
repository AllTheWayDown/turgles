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
    glUniform1f, glUniform1fv,
    glUniform2f, glUniform2fv,
    glUniform3f, glUniform3fv,
    glUniform4f, glUniform4fv,
    glUniform1i, glUniform1iv,
    glUniform2i, glUniform2iv,
    glUniform3i, glUniform3iv,
    glUniform4i, glUniform4iv,
    glUniformMatrix2fv,
    glUniformMatrix3fv,
    glUniformMatrix4fv,
    glGetUniformfv,
    glGetUniformiv,
    glGetActiveUniform,
    glGetActiveAttrib,

    glGetUniformLocation,
)

from turgles.memory import FFI, to_float_pointer, to_int_pointer


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
    }

    VSETTERS = {
        GL_FLOAT: glUniform1fv,
        GL_FLOAT_VEC2: glUniform2fv,
        GL_FLOAT_VEC3: glUniform3fv,
        GL_FLOAT_VEC4: glUniform4fv,
        GL_INT: glUniform1iv,
        GL_INT_VEC2: glUniform2iv,
        GL_INT_VEC3: glUniform3iv,
        GL_INT_VEC4: glUniform4iv,
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
        self.location = glGetUniformLocation(
            program_id, self.name.encode('utf8'))
        # unpack type constant
        self.item_type, self.length = self.UNIFORM_TYPES[self.type]
        if self.item_type == GLfloat:
            self.ctypes_converter = to_float_pointer
        elif self.item_type == GLint:
            self.ctypes_converter = to_int_pointer

        # ctypes type to use
        self.ctype = self.item_type * self.length
        # setup correct gl functions to access
        self._getter = self.GETTERS[self.item_type]
        self._setter = self.SETTERS.get(self.type, None)
        self._setterv = self.VSETTERS.get(self.type)

    def __eq__(self, other):
        return self.index == other.index

    def get(self):
        params = self.ctype(*([0.0] * self.length))
        self._getter(self.program_id, self.location, params)
        return params

    def set(self, *data):
        n = len(data)
        assert data
        if n > 1 or self.length == 1:
            # use non-array setter
            if n != self.length:
                raise UniformError("Uniform '%s' is of length %d, not %d" % (
                    self.name, self.length, len(data)))
            self._setter(self.location, *data)
        else:
            # use array based setter
            data = data[0]
            if len(data) != self.length * self.size:
                raise UniformError("uniform '%s' is of length %d, not %d" % (
                    self.name, self.length, len(data)))
            if isinstance(data, FFI.CData):
                cdata = self.ctypes_converter(data)
            else:
                # WARNING copies data, because ctypes. Send ffi data for speed
                cdata = self.ctype(*data)
            self._setterv(self.location, self.size, GL_FALSE, cdata)

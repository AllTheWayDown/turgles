from ctypes import byref, c_int, pointer, create_string_buffer
from gles20 import *  # NOQA

from util import (
    convert_to_cstring,
    get_program_log,
    get_shader_log,
    ShaderError,
)


def get_uniform_data(program_id, name):
    """Gets the metadata for a uniform variable"""
    name = name.encode('ascii')
    index = glGetUniformLocation(program_id, name)
    n = 64
    bufsize = GLsizei(n)
    length = pointer(GLsizei(0))
    size = pointer(GLint(0))
    type = pointer(GLenum(0))
    uname = create_string_buffer(n)
    glGetActiveUniform(program_id, index, bufsize, length, size, type, uname)
    assert name == uname.value
    return Uniform(name, index, size[0], type[0])


class Uniform(object):
    """Metadata for a uniform shader variable"""

    UNIFORM_TYPES = {
        GL_FLOAT_VEC2: (GLfloat, 2),
        GL_FLOAT_VEC3: (GLfloat, 3),
        GL_FLOAT_VEC4: (GLfloat, 4),
        GL_INT_VEC2: (GLint, 2),
        GL_INT_VEC3: (GLint, 3),
        GL_INT_VEC4: (GLint, 4),
        GL_BOOL_VEC2: (GLboolean, 2),
        GL_BOOL_VEC3: (GLboolean, 3),
        GL_BOOL_VEC4: (GLboolean, 4),
        GL_FLOAT_MAT2: (GLfloat, 2 * 2),
        GL_FLOAT_MAT3: (GLfloat, 3 * 3),
        GL_FLOAT_MAT4: (GLfloat, 4 * 4),
    }

    def __init__(self, name, index, size, type_):
        self.name = name
        self.index = index
        self.size = size
        self.type = type_
        self.gl_type, self.length = self.UNIFORM_TYPES.get(type_, (None, None))
        if not self.gl_type:
            raise ShaderError("Unknown uniform type: %s" % type_)
        self.ctype = self.gl_type * self.length

    def __eq__(self, other):
        return self.index == other.index

    def cvalue(self, *data):
        """Convert values in data to approriate c type"""
        return self.ctype(*(data[:self.length]))


class ShaderVariables(object):
    """Cached storage for shader variables"""
    SETTERS = {
        (GLfloat, 1): glUniform1f,
        (GLfloat, 2): glUniform2f,
        (GLfloat, 3): glUniform3f,
        (GLfloat, 4): glUniform4f,
        (GLint, 1): glUniform1i,
        (GLint, 2): glUniform2i,
        (GLint, 3): glUniform3i,
        (GLint, 4): glUniform4i,
    }

    GETTERS = {
        GLfloat: glGetUniformfv,
        GLint: glGetUniformiv,
    }

    def __init__(self, program_id):
        self.id = program_id
        self.variables = {}

    def get_uniform(self, name):
        uniform = self.variables.get(name, None)
        if uniform is None:
            uniform = get_uniform_data(self.id, name)
            self.variables[name] = uniform
        return uniform

    def __getitem__(self, key):
        uniform = self.get_uniform(key)
        params = uniform.cvalue(0.0, 0.0, 0.0, 0.0)
        get = self.GETTERS[uniform.gl_type]
        get(self.id, uniform.index, params)
        return params

    def __setitem__(self, key, value):
        uniform = self.get_uniform(key)
        data = uniform.cvalue(*value)
        set = self.SETTERS[(uniform.gl_type, uniform.length)]
        set(uniform.index, *data)


class Program:
    """Shader program abstraction"""

    def __init__(self, vertex, fragment):
        self.id = glCreateProgram()
        self.create_shader(vertex, GL_VERTEX_SHADER)
        self.create_shader(fragment, GL_FRAGMENT_SHADER)
        self.compile()
        self.uniforms = ShaderVariables(self.id)
        self.attributes = ShaderVariables(self.id)

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

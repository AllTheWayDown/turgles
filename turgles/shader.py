from ctypes import (
    byref,
    c_int,
    pointer,
)
from turgles import gl
from turgles.glutil import (
    convert_to_cstring,
    get_program_log,
    get_shader_log,
    load_uniform_data,
    ShaderError,
)
from turgles.memory import to_pointer, size_in_bytes

TYPEMAP = {
    gl.GLbyte:   (gl.GL_BYTE, 1),
    gl.GLubyte:  (gl.GL_UNSIGNED_BYTE, 1),
    gl.GLshort:  (gl.GL_SHORT, 2),
    gl.GLushort: (gl.GL_UNSIGNED_SHORT, 2),
    gl.GLint:    (gl.GL_INT, 4),
    gl.GLuint:   (gl.GL_UNSIGNED_INT, 4),
    gl.GLfloat:  (gl.GL_FLOAT, 4)
}


class Uniform(object):
    """A shader uniform variable.

    Provides some convienices to set/get uniforms"""

    UNIFORM_TYPES = {
        gl.GL_FLOAT: (gl.GLfloat, 1),
        gl.GL_FLOAT_VEC2: (gl.GLfloat, 2),
        gl.GL_FLOAT_VEC3: (gl.GLfloat, 3),
        gl.GL_FLOAT_VEC4: (gl.GLfloat, 4),
        gl.GL_INT: (gl.GLint, 1),
        gl.GL_INT_VEC2: (gl.GLint, 2),
        gl.GL_INT_VEC3: (gl.GLint, 3),
        gl.GL_INT_VEC4: (gl.GLint, 4),
        # TODO
        gl.GL_BOOL: (gl.GLboolean, 1),
        gl.GL_BOOL_VEC2: (gl.GLboolean, 2),
        gl.GL_BOOL_VEC3: (gl.GLboolean, 3),
        gl.GL_BOOL_VEC4: (gl.GLboolean, 4),
        gl.GL_FLOAT_MAT2: (gl.GLfloat, 2 * 2),
        gl.GL_FLOAT_MAT3: (gl.GLfloat, 3 * 3),
        gl.GL_FLOAT_MAT4: (gl.GLfloat, 4 * 4),
    }

    SETTERS = {
        gl.GL_FLOAT: gl.Uniform1f,
        gl.GL_FLOAT_VEC2: gl.Uniform2f,
        gl.GL_FLOAT_VEC3: gl.Uniform3f,
        gl.GL_FLOAT_VEC4: gl.Uniform4f,
        gl.GL_INT: gl.Uniform1i,
        gl.GL_INT_VEC2: gl.Uniform2i,
        gl.GL_INT_VEC3: gl.Uniform3i,
        gl.GL_INT_VEC4: gl.Uniform4i,
    }

    GETTERS = {
        gl.GLfloat: gl.GetUniformfv,
        gl.GLint: gl.GetUniformiv,
    }

    def __init__(self, program_id, index):
        self.program_id = program_id
        self.index = index
        self.size, self.type, self.name = load_uniform_data(program_id, index)
        # unpack type constant
        self.item_type, self.length = self.UNIFORM_TYPES[self.type]
        # ctypes type to use
        self.ctype = self.item_type * self.length
        # setup correct gl. functions to access
        self._getter = self.GETTERS[self.item_type]
        self._setter = self.SETTERS[self.type]

    def __eq__(self, other):
        return self.index == other.index

    def get(self):
        params = self.ctype(*([0.0] * self.length))
        self._getter(self.program_id, self.index, params)
        return params

    def set(self, *data):
        if len(data) != self.length:
            raise ShaderError("Uniform '%s' is of length %d, not %d" % (
                self.name, self.length, len(data)))
        self._setter(self.index, *data)


class Buffer(object):
    """Generic buffer abstraction.

    Creation, binding and loading of GPU buffers.
    """

    def __init__(self, array_type, element_type, draw_type):
        self.array_type = array_type
        self.element_type = element_type
        self.element_flag, self.element_size = TYPEMAP[element_type]
        self.draw_type = draw_type

        self.id = gl.GLuint()
        gl.GenBuffers(1, self.id)

    def bind(self):
        gl.BindBuffer(self.array_type, self.id)

    def unbind(self):
        """Same for all buffer types"""
        gl.BindBuffer(self.array_type, 0)

    def load(self, data, n=None):
        """Data is cffi array"""
        self.bind()
        gl.BufferData(
            self.array_type,
            size_in_bytes(data),
            to_pointer(data),
            self.draw_type)
        self.unbind()


class VertexBuffer(Buffer):
    """A VBO object to store vertex/model data.

    Specialisation of Buffer for attribute data, provides convient way to use
    gl.VertexAttribPointer, via set().
    """

    def __init__(self, element_type, draw_type):
        super(VertexBuffer, self).__init__(
            gl.GL_ARRAY_BUFFER, element_type, draw_type)

    def set(self,
            index,
            interpolate=gl.GL_FALSE,
            stride=0,
            offset=0,
            divisor=None):
        self.bind()
        gl.EnableVertexAttribArray(index)
        gl.VertexAttribPointer(
            index,
            self.element_size,
            self.element_flag,
            interpolate,
            stride,
            offset
        )
        if divisor is not None:
            gl.VertexAttribDivisor(index, divisor)


class Program:
    """Shader program abstraction.

    Loads/compiles/links the shaders, and handles any errors.
    """

    def __init__(self, vertex, fragment):
        self.id = gl.CreateProgram()
        self.create_shader(vertex, gl.GL_VERTEX_SHADER)
        self.create_shader(fragment, gl.GL_FRAGMENT_SHADER)
        self.compile()
        self.bind()

        count = pointer(gl.GLint(0))

        self.uniforms = {}
        gl.GetProgramiv(self.id, gl.GL_ACTIVE_UNIFORMS, count)
        for index in range(count[0]):
            uniform = Uniform(self.id, index)
            self.uniforms[uniform.name] = uniform

        self.unbind()

    def create_shader(self, src, type):
        shader_id = gl.CreateShader(type)
        gl.ShaderSource(shader_id, 1, byref(convert_to_cstring(src)), None)
        gl.CompileShader(shader_id)

        status = c_int(0)
        gl.GetShaderiv(
            shader_id, gl.GL_OBJECT_COMPILE_STATUS_ARB, byref(status))

        if not status:
            raise ShaderError(get_shader_log(shader_id))
        else:
            gl.AttachShader(self.id, shader_id)

    def compile(self):
        gl.LinkProgram(self.id)
        status = c_int(0)
        gl.GetProgramiv(self.id, gl.GL_LINK_STATUS, byref(status))
        if not status:
            raise ShaderError(get_program_log(self.id))

    def bind(self):
        gl.UseProgram(self.id)

    def unbind(self):
        gl.UseProgram(0)

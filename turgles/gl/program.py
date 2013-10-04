from ctypes import (
    c_char_p,
    c_char,
    c_int,
    byref,
    cast,
    POINTER,
    pointer,
    create_string_buffer,
)

from turgles.gl.api import (
    GL_ACTIVE_UNIFORMS,
    glAttachShader,
    glCompileShader,
    glCreateProgram,
    glCreateShader,
    GL_FRAGMENT_SHADER,
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    GL_INFO_LOG_LENGTH,
    GLint,
    glLinkProgram, glUseProgram,
    GL_LINK_STATUS,
    GL_OBJECT_COMPILE_STATUS_ARB,
    glShaderSource,
    GL_VERTEX_SHADER,
)

from turgles.gl.uniform import Uniform


class ShaderError(Exception):
    pass


class VertexShaderError(ShaderError):
    pass


class FragmentShaderError(ShaderError):
    pass


class ShaderLinkerError(ShaderError):
    pass


def convert_to_cstring(pystring):
    utf_string = pystring.encode('utf8')
    return cast(c_char_p(utf_string), POINTER(c_char))


def _make_gl_logger(getLength, getInfoLog):
    def get_log(id):
        log_length = c_int(0)
        getLength(id, GL_INFO_LOG_LENGTH, byref(log_length))
        log = create_string_buffer(log_length.value)
        getInfoLog(id, log_length.value, None, log)
        return log.value
    return get_log


get_shader_log = _make_gl_logger(glGetShaderiv, glGetShaderInfoLog)
get_program_log = _make_gl_logger(glGetProgramiv, glGetProgramInfoLog)


class Program:
    """Shader program abstraction.

    Loads/compiles/links the shaders, and handles any errors.
    """

    def __init__(self, vertex, fragment):
        self.id = glCreateProgram()
        self.create_shader(vertex, GL_VERTEX_SHADER)
        self.create_shader(fragment, GL_FRAGMENT_SHADER)
        self.compile()
        self.bind()

        count = pointer(GLint(0))

        self.uniforms = {}
        glGetProgramiv(self.id, GL_ACTIVE_UNIFORMS, count)
        for index in range(count[0]):
            uniform = Uniform(self.id, index)
            self.uniforms[uniform.name] = uniform

        #for v in self.uniforms.values():
        #    print(v.name, v.size, v.length)

        self.unbind()

    def create_shader(self, src, type):
        shader_id = glCreateShader(type)
        glShaderSource(shader_id, 1, byref(convert_to_cstring(src)), None)
        glCompileShader(shader_id)

        status = c_int(0)
        glGetShaderiv(
            shader_id, GL_OBJECT_COMPILE_STATUS_ARB, byref(status))

        if not status:
            if type == GL_VERTEX_SHADER:
                exc = VertexShaderError
            else:
                exc = FragmentShaderError
            raise exc(get_shader_log(shader_id))
        else:
            glAttachShader(self.id, shader_id)

    def compile(self):
        glLinkProgram(self.id)
        status = c_int(0)
        glGetProgramiv(self.id, GL_LINK_STATUS, byref(status))
        if not status:
            raise ShaderLinkerError(get_program_log(self.id))

    def bind(self):
        glUseProgram(self.id)

    def unbind(self):
        glUseProgram(0)

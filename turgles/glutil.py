from ctypes import *  # NOQA
from turgles.gles20 import *  # NOQA


class ShaderError(Exception):
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

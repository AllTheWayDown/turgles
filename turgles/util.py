from ctypes import *  # NOQA
from gles20 import *  # NOQA


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

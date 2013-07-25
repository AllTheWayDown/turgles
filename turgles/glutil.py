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

from turgles import gl


class ShaderError(Exception):
    pass


def convert_to_cstring(pystring):
    utf_string = pystring.encode('utf8')
    return cast(c_char_p(utf_string), POINTER(c_char))


def _make_gl_logger(getLength, getInfoLog):
    def get_log(id):
        log_length = c_int(0)
        getLength(id, gl.GL_INFO_LOG_LENGTH, byref(log_length))
        log = create_string_buffer(log_length.value)
        getInfoLog(id, log_length.value, None, log)
        return log.value
    return get_log


get_shader_log = _make_gl_logger(gl.GetShaderiv, gl.GetShaderInfoLog)
get_program_log = _make_gl_logger(gl.GetProgramiv, gl.GetProgramInfoLog)


def _load_variable(func, program_id, index):
    """Loads the meta data for a uniform or attribute"""
    n = 64  # max name length TODO: read from card
    bufsize = gl.GLsizei(n)
    length = pointer(gl.GLsizei(0))
    size = pointer(gl.GLint(0))
    type = pointer(gl.GLenum(0))
    uname = create_string_buffer(n)
    func(program_id, index, bufsize, length, size, type, uname)
    return size[0], type[0], uname.value.decode('utf8')


def load_uniform_data(program_id, index):
    return _load_variable(gl.GetActiveUniform, program_id, index)


def load_attribute_data(program_id, index):
    return _load_variable(gl.GetActiveAttrib, program_id, index)

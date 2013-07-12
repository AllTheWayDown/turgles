import atexit
import functools
from time import time
from collections import defaultdict
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

MEASUREMENTS = defaultdict(list)


class measure(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            start = time()
            result = func(*args, **kwargs)
            MEASUREMENTS[self.name].append(time() - start)
        return decorator

    def __enter__(self):
        self.start = time()

    def __exit__(self, *exc_info):
        MEASUREMENTS[self.name].append(time() - self.start)


@atexit.register
def print_measurements():
    import pyglet
    print('fps: {:.3f}'.format(pyglet.clock.get_fps()))

    data = []
    for name, values in MEASUREMENTS.items():
        values.sort()
        mean, median, graph = stats(values)
        data.append((median, mean, graph, name))
    data.sort()
    for median, mean, graph, name in data:
        print("{}: {:.3f} ms\n{}".format(name, median*1000, graph))


def stats(data):
    data.sort()
    dmin = data[0]
    dmax = data[-1]
    mean = sum(data) / len(data)
    median = data[len(data) // 2]
    diff = dmax - dmin

    bins = 64

    hist = [0] * bins
    for num in data:
        bin = int((num - dmin) / diff * bins)
        bin = min(bin, bins-1)
        hist[bin] += 1

    hmax = max(hist)

    ticks = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    graph = []
    for count in hist:
        if count == 0:
            graph.append(' ')
        else:
            index = int(count / hmax * 8)
            index = min(index, 7)
            graph.append(ticks[index])

    return mean, median, ''.join(graph)

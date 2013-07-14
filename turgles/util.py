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
    print('FPS: {:.3f}'.format(pyglet.clock.get_fps()))
    data = []
    for name, values in MEASUREMENTS.items():
        values.sort()
        mean, median, dmin, dmax, graph = stats(values)
        data.append((median, mean, dmin, dmax, graph, name))
    data.sort()
    hd  = "{:10}| {:>10} | {:>5} {:^32} {:>5}|"
    fmt = "{:10}: {:7.1f} ms [ {:5.1f} {} {:5.1f}]"

    print(hd.format('name', 'median', 'min', 'histogram', 'max'))
    print('-' * 64)
    for median, mean, dmin, dmax, graph, name in data:
        print(fmt.format(name, median * 1000, dmin * 1000, graph, dmax * 1000))


def stats(data, bins=32, outliers=2):
    data.sort()
    outlier_min = data[0]
    outlier_max = data[-1]
    clean_data = data[outliers:-outliers]
    dmax = clean_data[-1]
    dmin = clean_data[0]
    dmax = clean_data[-1]

    mean = sum(clean_data) / len(clean_data)
    median = data[len(clean_data) // 3]
    diff = dmax - dmin

    hist = [0] * bins
    for num in clean_data:
        bin = int((num - dmin) / diff * bins)
        bin = min(bin, bins-1)
        hist[bin] += 1

    maxcount = max(hist)

    ticks = ['_', '▂', '▃', '▄', '▅', '▆', '▇']  #, '█']

    graph = []
    for count in hist:
        if count == 0:
            graph.append(' ')
        elif count == 1:
            graph.append(ticks[0])
        else:
            index = int(count / maxcount * 7)
            index = min(index, 6)
            graph.append(ticks[index])

    return mean, median, outlier_min, outlier_max, ''.join(graph)

from math import sin, cos, pi
from array import array


def generate_circle_geometry(n):
    angles = [ -pi/2 + (pi * (i/n)) for i in range(1, n-1)]
    yield -1.0
    yield 0.0
    for angle in angles:
        c = cos(angle)
        s = sin(angle)
        yield s
        yield c
        yield s
        yield -c
    yield 1.0
    yield 0.0



# generated from shapes in turtle module
# normalised to -1.0 <-> 1.0 and rotated right by 90 degrees
turtle_shapes = {
    'turtle': {
        'vertex': (
            1.000000, 0.000000,
            0.875000, 0.125000,
            0.625000, 0.062500,
            0.437500, 0.250000,
            0.562500, 0.437500,
            0.500000, 0.562500,
            0.312500, 0.375000,
            0.062500, 0.437500,
            -0.187500, 0.312500,
            -0.375000, 0.500000,
            -0.500000, 0.375000,
            -0.312500, 0.250000,
            -0.437500, 0.000000,
            -0.312500, -0.250000,
            -0.500000, -0.375000,
            -0.375000, -0.500000,
            -0.187500, -0.312500,
            0.062500, -0.437500,
            0.312500, -0.375000,
            0.500000, -0.562500,
            0.562500, -0.437500,
            0.437500, -0.250000,
            0.625000, -0.062500,
            0.875000, -0.125000,
        ),
        'index': (
            0, 1, 23,
            1, 22, 23,
            2, 22, 1,
            2, 3, 22,
            3, 21, 22,
            3, 4, 6,
            6, 4, 5,
            3, 6, 7,
            3, 7, 21,
            7, 8, 21,
            8 ,16, 21,
            8, 9, 11,
            9, 10, 11,
            11, 13, 8,
            8, 13, 16,
            11, 12, 13,
            13, 14, 15,
            13, 15, 16,
            16, 18, 21,
            16, 17, 18,
            18, 19, 20,
            18, 20, 21,
        ),
    },
    'square': {
        'vertex': (
            -1.000000, -1.000000,
            1.000000, -1.000000,
            1.000000, 1.000000,
            -1.000000, 1.000000,
        ),
        'index': (
            0, 1, 2,
            0, 2, 3
        ),
    },
    'circle': {
        'vertex': (
            0.000000, -1.000000,
            0.309000, -0.951000,
            0.588000, -0.809000,
            0.809000, -0.588000,
            0.951000, -0.309000,
            1.000000, 0.000000,
            0.951000, 0.309000,
            0.809000, 0.588000,
            0.588000, 0.809000,
            0.309000, 0.951000,
            0.000000, 1.000000,
            -0.309000, 0.951000,
            -0.588000, 0.809000,
            -0.809000, 0.588000,
            -0.951000, 0.309000,
            -1.000000, 0.000000,
            -0.951000, -0.309000,
            -0.809000, -0.588000,
            -0.588000, -0.809000,
            -0.309000, -0.951000,
        ),
        'index': (
            0, 1, 19,
            19, 1, 2,
            19, 2, 18,
            18, 2, 3,
            18, 3, 17,
            17, 3, 4,
            17, 4, 16,
            16, 4, 5,
            16, 5, 15,
            15, 5, 6,
            15, 6, 14,
            14, 6, 7,
            14, 7, 13,
            13, 7, 8,
            13, 8, 12,
            12, 8, 9,
            12, 9, 11,
            11, 9, 10,
        ),
    },
    'triangle': {
        'vertex': (
            -0.499567, -0.865801,
            1.000000, 0.000000,
            -0.499567, 0.865801,
        ),
        'index': (0, 1, 2)
    },
    'classic': {
        'vertex': (
            0.000000, 0.000000,
            -1.000000, 0.555556,
            -0.777778, 0.000000,
            -1.000000, -0.555556,
        ),
        'index': (
            0, 1, 2,
            0, 2, 3,
        ),
    },
    'arrow': {
        'vertex': (
            0.000000, 1.000000,
            0.000000, -1.000000,
            1.000000, 0.000000,
        ),
        'index': (0, 1, 2)
    },
}


class TurtleGeometry(object):

    def __init__(self, vertices, indices):
        self.vertices = array('f', vertices)
        self.indices = array('H', indices)
        self.num_vertex = len(indices)
        self.indices_pointer, self.indices_length = self.indices.buffer_info()

    @classmethod
    def make_vec4(cls, data):
        """transforms an array of 2d coords into 4d"""
        it = iter(data)
        while True:
            yield next(it)  # x
            yield next(it)  # y
            yield 0.0       # z
            yield 1.1       # w

    @classmethod
    def load_shape(cls, shape):
        turtle_shape = turtle_shapes[shape]
        return cls(list(cls.make_vec4(turtle_shape['vertex'])),
                   turtle_shape['index'])

    @classmethod
    def load_file(cls, path):
        #TODO
        pass

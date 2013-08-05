from turgles.memory import (create_vertex_buffer, create_index_buffer)

# generated from shapes in turtle module
# normalised to -1.0 <-> 1.0 and rotated right by 90 degrees
STANDARD_SHAPE_POLYGONS = {
    'turtle': {
        'scale': 16.0,
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
            8, 16, 21,
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
        'scale': 10.0,
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
        'scale': 10.0,
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
        'scale': 11.55,
        'vertex': (
            -0.499567, -0.865801,
            1.000000, 0.000000,
            -0.499567, 0.865801,
        ),
        'index': (0, 1, 2)
    },
    'classic': {
        'scale': 9.0,
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
        'scale': 10.0,
        'vertex': (
            0.000000, 1.000000,
            0.000000, -1.000000,
            1.000000, 0.000000,
        ),
        'index': (0, 1, 2)
    },
}


class TurtleGeometry(object):
    """Manages the mesh for a turtle.

    Uses cffi to create c-arrays for storing vertices, indexes, and normals.
    """

    def __init__(self, scale, vertices, indices):
        self.scale = scale
        self.vertices = create_vertex_buffer(vertices)
        self.indices = create_index_buffer(indices)

        self.indices_outline = create_index_buffer(
            list(range(len(vertices)//4)))
        self.num_vertex = len(indices)

    @classmethod
    def load_file(cls, path):
        """Loads from file"""


def convert_vec2_to_vec4(data):
    """transforms an array of 2d coords into 4d"""
    it = iter(data)
    while True:
        yield next(it)  # x
        yield next(it)  # y
        yield 0.0       # z
        yield 1.0       # w


# Initialise standard shapes on import
SHAPES = {}
for name, data in STANDARD_SHAPE_POLYGONS.items():
    geom = TurtleGeometry(
        data['scale'],
        list(convert_vec2_to_vec4(data['vertex'])),
        data['index'],
    )
    SHAPES[name] = geom

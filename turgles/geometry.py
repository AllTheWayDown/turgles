from math import fabs

from turgles.memory import (create_vertex_buffer, create_index_buffer)

# generated from shapes in turtle module
# normalised to -1.0 <-> 1.0 and rotated right by 90 degrees
STANDARD_SHAPE_POLYGONS = {
    'turtle': {
        'scale': 20.0,
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






        'exclude': (
            1, 0, 0,
            0, 1, 1,
            1, 0, 1,
            1, 1, 0,
            0, 1, 1,
            1, 1, 0,
            0, 0, 1,
            0, 1, 1,
            1, 1, 1,
            1, 1, 0,
            1, 1, 1,
            1, 1, 0,
            0, 1, 0,
            1, 1, 1,
            1, 1, 1,
            0, 1, 0,
            0, 1, 0,
            0, 1, 1,
            1, 1, 1,
            0, 1, 0,
            0, 1, 0,
            0, 1, 1,
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
        'exclude': (
            0, 1, 0,
            0, 0, 1,
        )
    },
    'circle': {
        'scale': 10.0,
        'vertex': (
            0.000000,  0.000000,
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
            0,  1,  2,
            0,  2,  3,
            0,  3,  4,
            0,  4,  5,
            0,  5,  6,
            0,  6,  7,
            0,  7,  8,
            0,  8,  9,
            0,  9,  10,
            0, 10,  11,
            0, 11,  12,
            0, 12,  13,
            0, 13,  14,
            0, 14,  15,
            0, 15,  16,
            0, 16,  17,
            0, 17,  18,
            0, 18,  19,
            0, 19,  20,
            0, 20,  1,
        ),
        'exclude': (
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
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
        'scale': 14.0,
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
        'exclude': (
            0, 1, 0,
            0, 0, 1,
        )
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

    def __init__(self, scale, vertices, indices, exclude):
        self.scale = scale

        self.vertices = create_vertex_buffer(vertices)
        self.indices = create_index_buffer(indices)
        self.num_vertex = len(indices)

        self.edges = self.calculate_edges(exclude)

    def calculate_edges(self, excludes):
        """Builds a vertex list adding barycentric coordinates to each vertex.

        Used to draw turtle borders efficiently, specialised to draw only the
        some edges. See below for references.

        http://stackoverflow.com/questions/18035719/drawing-a-border-on-a-2d-polygon-with-a-fragment-shader  # NOQA
        http://codeflow.org/entries/2012/aug/02/easy-wireframe-display-with-barycentric-coordinates/  # NOQA
        http://strattonbrazil.blogspot.co.uk/2011/09/single-pass-wireframe-rendering_11.html  # NOQA
        """
        edges = []
        MEW = 100.0
        if excludes is None:
            excludes = [0] * len(self.indices)
        for i in range(0, len(self.indices), 3):  # each triangle
            i0 = self.indices[i+0] * 4
            i1 = self.indices[i+1] * 4
            i2 = self.indices[i+2] * 4
            e0 = excludes[i+0]
            e1 = excludes[i+1]
            e2 = excludes[i+2]
            p0 = self.vertices[i0:i0+4]
            p1 = self.vertices[i1:i1+4]
            p2 = self.vertices[i2:i2+4]
            v0 = self.vec2minus(p2, p1)
            v1 = self.vec2minus(p2, p0)
            v2 = self.vec2minus(p1, p0)
            area = fabs(v1[0]*v2[1] - v1[1] * v2[0])
            c0 = (area/self.magnitude(v0), e1 * MEW, e2 * MEW)
            c1 = (e0 * MEW, area/self.magnitude(v1), e2 * MEW)
            c2 = (e0 * MEW, e1 * MEW, area/self.magnitude(v2))
            edges.extend(p0)
            edges.extend(c0)
            edges.extend(p1)
            edges.extend(c1)
            edges.extend(p2)
            edges.extend(c2)
        return create_vertex_buffer(edges)

    def vec2minus(self, a, b):
        return a[0] - b[0], a[1] - b[1]

    def magnitude(self, v):
        return (v[0]**2 + v[1]**2) ** 0.5

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
        data.get('exclude'),
    )
    SHAPES[name] = geom

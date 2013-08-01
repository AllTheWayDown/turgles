from unittest import TestCase

from turgles.gl.program import Program, ShaderError

VERTEX = """
uniform vec4 model;
attribute vec4 VERTEX;

void main()
{
    gl_Position = model * VERTEX;
}
"""

FRAGMENT = """
void main()
{
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
"""


class ProgramTestCase(TestCase):

    def test_simple_shaders_compile(self):
        p = Program(VERTEX, FRAGMENT)
        self.assertEqual(len(p.uniforms), 1)
        self.assertIn('model', p.uniforms)

    def test_bad_VERTEX_shader(self):
        with self.assertRaises(ShaderError):
            Program("", FRAGMENT)

    def test_bad_fragment_shader(self):
        with self.assertRaises(ShaderError):
            Program(VERTEX, "")


class ShadersTestCase(TestCase):

    def assert_compiles(self, vertex=None, fragment=None):
        if vertex is None:
            vertex = VERTEX
        else:
            with open(vertex) as f:
                vertex = f.read()
        if fragment is None:
            fragment = FRAGMENT
        else:
            with open(fragment) as f:
                fragment = f.read()

        try:
            Program(vertex, fragment)
        except ShaderError as e:
            self.fail("shader failed to compile: %s" % e)

    def test_turtle1_vertex_shader_compiles(self):
        self.assert_compiles(vertex='turgles/shaders/turtles.vert')

    def test_turtle_fragment_shader_compiles(self):
        self.assert_compiles(
            vertex='turgles/shaders/turtles.vert',
            fragment='turgles/shaders/turtles.frag',
        )

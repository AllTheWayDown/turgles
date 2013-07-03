from random import randint, random, expovariate
from math import radians, sin, cos, pi
from time import time
import pyglet
from ctypes import sizeof

from array import array
from multiprocessing import Array

from gles20 import *  # NOQA

from shader import Program, Buffer

from geometry import turtle_shapes


TURTLES = array('f')

class Turtle(object):
    """A view of a single turtle in the massive list of turtles."""
    __slots__ = ('_turtles', '_num', 'X', 'Y', 'ANGLE', 'SIZE')

    def __init__(self, turtles, num):
        self._turtles = turtles
        self._num = num
        self.X, self.Y, self.ANGLE, self.SIZE = (num + i for i in range(4))

    def getx(self):
        return self._turtles[self.X]
    def setx(self, x):
        self._turtles[self.X] = x
    x = property(getx, setx)

    def gety(self):
        return self._turtles[self.Y]
    def sety(self, y):
        self._turtles[self.Y] = y
    y = property(gety, sety)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


def wrapper(data, index):
    class descriptor(object):
        def __set__(self, instance, value):
            data[index] = value
        def __get__(self, instance, owner):
            return data[index]
    return descriptor()


def get_turtle(data, n):
    class Turtle(object):
        x = wrapper(data, n)
        y = wrapper(data, n + 1)
        angle = wrapper(data, n + 2)
        size = wrapper(data, n + 3)
    return Turtle()


num_turtles = 1000000
turtles = array.array("f", range(num_turtles * 4))


def bench(f):
    objs = [f(turtles, i * 4) for i in range(num_turtles)]
    start = time()
    for t in objs:
        t.x += 1
        t.y += 1
    return time() - start

def direct():
    t = turtles
    x = range(num_turtles)
    start = time()
    for i in x:
        n = i * 4
        t[n] += 1
        t[n + 1] += 1
    return time() - start


turtles = array.array("f", range(num_turtles * 4))
print(bench(TurtleView))
#turtles = array.array("f", range(num_turtles * 4))
#print(bench(get_turtle))
turtles = array.array("f", range(num_turtles * 4))
print(direct())







class World(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.half_width = width / 2
        self.half_height = height / 2
        self.array = array('f')

    def add_turtle(self, x=None, y=None, shape="classic", size=1.0):
        turtle = self._generate_turtles(1, shape, size, x, y)

    def add_turtles(self, n, shape="classic", size=1.0):
        turtle = self._generate_turtles(n, shape, size)

    def _generate



turtle_data_size = 4
def gen_world():
    for i in range(num_turtles):
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield random() * 360.0
        yield turtle_size  # * random() + 1.0

turtle_model = array('f', list(gen_world())) #, lock=False)
turtle_shape = turtle_shapes[shape]


turtle_geom = array('f', turtle_shape['vertex'])

turtle_index = array('B', turtle_shape['index'])
indices_pointer, indicies_length = turtle_index.buffer_info()

num_vertex = len(turtle_index)

program = Program(
'''
    uniform vec2 scale;
    attribute vec2 shape_vertex;
    attribute vec4 turtle;

    void main()
    {
        vec4 vertex = vec4(
            shape_vertex.x,
            shape_vertex.y,
            0.0,
            1.0
        );
        float theta = radians(turtle.z);
        float ct = cos(theta);
        float st = sin(theta);
        float x = turtle.w / scale.x;
        float y = turtle.w / scale.y;
        mat4 model = mat4(ct * x, -st * y,  0.0, turtle.x / scale.x,
                          st * x,  ct * y,  0.0, turtle.y / scale.y,
                          0.0, 0.0, 0.0, 0.0,
                          0.0, 0.0, 0.0, 1.0);
        gl_Position = vertex * model;
    }''',

'''
    void main()
    {
        gl_FragColor = vec4(0.1, 0.1, 0.1, 0.1);
    }'''
)

glClearColor(1.0, 1.0, 1.0, 0.0)

vertex_attr = glGetAttribLocation(program.id, b"shape_vertex")
turtle_attr = glGetAttribLocation(program.id, b"turtle")


# initialise
program.bind()
program.uniforms['scale'].set(half_size, half_size)
# TODO view matrix

vertices = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STATIC_DRAW)
vertices.load(turtle_geom)
vertices.bind(vertex_attr, size=2)

turtles = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STREAM_READ)
# initial load
turtles.load(turtle_model)

fps_display = pyglet.clock.ClockDisplay()

draw_total = 0.0
draw_count = 0
update_total = 0.0
update_count = 0
load_total = 0.0
load_count = 0

@window.event
def on_draw():
    global draw_total, draw_count
    x = time()
    window.clear()
    turtles.bind(turtle_attr, size=4, divisor=1)
    glDrawElementsInstanced(
        GL_TRIANGLES, indicies_length, GL_UNSIGNED_BYTE, indices_pointer,
        num_turtles)
    draw_total += time() -x
    draw_count += 1

speed = 50.0
degrees = 15.0
lambd = 1.0 / degrees
half_degrees = degrees / 2

def update(dt):
    global update_total, update_count, load_total, load_count
    xtt = time()
    magnitude = speed * dt
    for t in range(num_turtles):
        x = t * turtle_data_size
        y = x + 1
        angle = x + 2

        turtle_model[angle] += expovariate(lambd) - degrees
        theta = radians(turtle_model[angle])
        dy = magnitude * sin(theta)
        dx = magnitude * cos(theta)
        turtle_model[x] += dx
        turtle_model[y] += dy
        if turtle_model[x] > half_size:
            turtle_model[x] -= world_size
        elif turtle_model[x] < -half_size:
            turtle_model[x] += world_size
        if turtle_model[y] > half_size:
            turtle_model[y] -= world_size
        elif turtle_model[y] < -half_size:
            turtle_model[y] += world_size
    update_total += time() - xtt
    update_count += 1
    xtt = time()
    turtles.load(turtle_model)
    load_total += time() - xtt
    load_count += 1

pyglet.clock.schedule_interval(update, 1/30)

pyglet.app.run()

print('   fps: {:.3f}'.format(pyglet.clock.get_fps()))
print('  draw: {:.3f} ms'.format(draw_total / draw_count * 1000))
print('update: {:.3f} ms'.format(update_total / update_count * 1000))
print('  load: {:.3f} ms'.format(load_total / load_count * 1000))

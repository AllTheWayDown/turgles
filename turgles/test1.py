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

world_size = 800.0
half_size = world_size / 2
turtle_size = 10.0
num_turtles = 10000
shape = 'turtle'

window = pyglet.window.Window(width=int(world_size), height=int(world_size))

# world coords
turtle_data_size = 4
def gen_world():
    for i in range(num_turtles):
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield random() * 360.0
        yield turtle_size  # * random() + 1.0

turtle_model = array('f', list(gen_world())) #, lock=False)
program = Program(
    open('shaders/turtles.vert').read(),
    open('shaders/turtles.frag').read()
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
    for x in range(0, num_turtles * turtle_data_size, turtle_data_size):
        y = x + 1
        angle = x + 2

        if (abs(turtle_model[x]) > half_size or
            abs(turtle_model[y]) > half_size):
            turtle_model[angle] = (turtle_model[angle] + 180) % 360
        turtle_model[angle] += expovariate(lambd) - degrees
        theta = radians(turtle_model[angle])
        dy = magnitude * sin(theta)
        dx = magnitude * cos(theta)
        turtle_model[x] += dx
        turtle_model[y] += dy
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

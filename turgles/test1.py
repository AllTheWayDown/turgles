from random import randint, random, expovariate
from math import radians, sin, cos, pi
from time import time
import pyglet

from gles20 import *  # NOQA

from shader import Program, Buffer

world_size = 800.0
half_size = world_size / 2
turtle_size = 10.0
num_turtles = 1000

window = pyglet.window.Window(width=int(world_size), height=int(world_size))


turtle_geom_quad = [
    -1.0, -1.0, 0.0, 1.0,
    -1.0,  1.0, 0.0, 1.0,
     1.0, -1.0, 0.0, 1.0,
     1.0,  1.0, 0.0, 1.0,
]

turtle_geom_arrow = [
    -1.0,  1.0, 0.0, 1.0,
     1.0,  0.0, 0.0, 1.0,
    -0.5,  0.0, 0.0, 1.0,
    -1.0, -1.0, 0.0, 1.0,
]

turtle_geom_arrow2 = [
    -1.0,  1.0, 0.0, 1.0,
     1.0,  0.5, 0.0, 1.0,
    -0.5,  0.0, 0.0, 1.0,
     1.0,  -0.5, 0.0, 1.0,
    -1.0, -1.0, 0.0, 1.0,
]
# world coords
turtle_data_size = 4
def gen_world():
    for i in range(num_turtles):
        yield random() * world_size - half_size
        yield random() * world_size - half_size
        yield random() * 360.0
        yield 1.0

turtle_model = list(gen_world())

turtle_geom = turtle_geom_arrow2
num_vertex = len(turtle_geom) // 4
# same geom for all turtles, for now
turtle_geom_data = turtle_geom * len(turtle_model)
total_count = len(turtle_geom_data)

program = Program(
'''
    #define DEG_TO_RAD(x) (x) * 0.017453292519943295
    uniform vec4 scale;
    attribute vec4 vertex;
    attribute vec4 turtle;

    void main()
    {
        float theta = DEG_TO_RAD(turtle.z);
        float ct = cos(theta);
        float st = sin(theta);
        mat4 model = mat4(
            ct * scale.z, -st * scale.w,  0.0, turtle.x / scale.x,
            st * scale.z,  ct * scale.w,  0.0, turtle.y / scale.y,
            0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        );
        gl_Position = vertex * model;
    }''',

'''
    void main()
    {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
    }'''
)

glClearColor(1.0, 1.0, 1.0, 0.0)

vertex_attr = glGetAttribLocation(program.id, b"vertex")
turtle_attr = glGetAttribLocation(program.id, b"turtle")


# initialise
program.bind()
program.uniforms['scale'].set(
    half_size,  # x scale
    half_size,  # y scale
    turtle_size / half_size,  # turtle x size
    turtle_size / half_size,  # turtle y size
)
# TODO view matrix

vertices = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STATIC_DRAW)
vertices.load(turtle_geom_data)
vertices.bind(vertex_attr)

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
    turtles.bind(turtle_attr, turtle_data_size, divisor=1)
    glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, num_vertex, num_turtles)
    draw_total += time() -x
    draw_count += 1

speed = 50.0
degrees = 20.0
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
    update_total += time() -xtt
    update_count += 1
    xtt = time()
    turtles.load(turtle_model)
    load_total += time() - xtt
    load_count += 1

pyglet.clock.schedule_interval(update, 1/30)

pyglet.app.run()

print('draw', draw_total / draw_count * 1000)
print('update', update_total / update_count * 1000)
print('load', load_total / load_count * 1000)

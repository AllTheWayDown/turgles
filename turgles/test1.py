from random import randint, random, expovariate
from math import radians, sin, cos, pi
import pyglet

from gles20 import *  # NOQA

from shader import Program, Buffer

world_size = 800.0
half_size = world_size / 2
turtle_size = 5.0
num_turtles = 1000

window = pyglet.window.Window(width=int(world_size), height=int(world_size))


turtle_geom_quad = [
    -1.0, -1.0, 0.0, 1.0,
    -1.0,  1.0, 0.0, 1.0,
     1.0, -1.0, 0.0, 1.0,
     1.0,  1.0, 0.0, 1.0,
]

turtle_geom_arrow = [
    -1.0, -1.0, 0.0, 1.0,
     0.0,  1.0, 0.0, 1.0,
     0.0, -0.5, 0.0, 1.0,
     1.0, -1.0, 0.0, 1.0,
]

# world coords
def gen_world():
    return [
        [randint(-half_size, half_size),
         randint(-half_size, half_size),
         float(randint(0, 360)),
         turtle_size] for i in range(num_turtles)]

turtle_model = gen_world()



program = Program(
'''
    #define DEG_TO_RAD(x) (x) * 0.017453292519943295
    uniform vec4 turtle;
    uniform vec2 scale;
    attribute vec4 vertex;

    void main()
    {
        // adjust to turtle world view by rotating by 90
        float theta = DEG_TO_RAD(turtle.z - 90.0);
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
        gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
    }'''
)

glClearColor(1.0, 1.0, 1.0, 0.0)

vertex_attr = glGetAttribLocation(program.id, b"vertex")


# initialise
program.bind()
program.uniforms['scale'].set(half_size, half_size)

vertices = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STATIC_DRAW)
vertices.load(turtle_geom_arrow)
vertices.bind(vertex_attr)

turtle_set = program.uniforms['turtle'].set
fps_display = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    window.clear()
    for turtle in turtle_model:
        turtle_set(*turtle)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    print(pyglet.clock.get_fps())


speed = 50.0
degrees = 20.0
lambd = 1.0 / degrees
half_degrees = degrees / 2

def update(dt):
    magnitude = speed * dt
    for turtle in turtle_model:
        turtle[2] += expovariate(lambd) - degrees
        theta = radians(turtle[2])
        dy = magnitude * sin(theta)
        dx = magnitude * cos(theta)
        turtle[0] += dx
        turtle[1] += dy
        if turtle[0] > half_size:
            turtle[0] -= world_size
        elif turtle[0] < -half_size:
            turtle[0] += world_size
        if turtle[1] > half_size:
            turtle[1] -= world_size
        elif turtle[1] < -half_size:
            turtle[1] += world_size

pyglet.clock.schedule_interval(update, 0.025)

pyglet.app.run()

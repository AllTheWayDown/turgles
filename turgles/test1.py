from random import randint

import pyglet

from gles20 import *  # NOQA

from shader import Program
from buffer import Buffer

world_size = 400.0
turtle_size = 10.0
num_turtles = 50

window = pyglet.window.Window(width=400, height=400)


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


vertices = Buffer(GLfloat, GL_ARRAY_BUFFER, GL_STATIC_DRAW)
vertices.load(turtle_geom_arrow)

# world coords
turtle_model = [
    (randint(0, world_size - 10) - world_size / 2,
     randint(0, world_size - 10) - world_size / 2,
     float(randint(0, 360)),
     5.5) for i in range(num_turtles)]

turtle_data_size = len(turtle_model[0])


program = Program(
'''
    #define DEG_TO_RAD(x) (x) * 0.017453292519943295
    uniform vec4 turtle;
    uniform vec2 scale;
    attribute vec4 vertex;

    void main()
    {
        float theta = DEG_TO_RAD(turtle.z);
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
turtle_set = program.uniforms['turtle'].set
program.uniforms['scale'].set(200.0, 200.0)
program.unbind()

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    program.bind()
    vertices.bind()
    glEnableVertexAttribArray(vertex_attr)
    glVertexAttribPointer(vertex_attr, 4, GL_FLOAT, GL_FALSE, 0, 0)

    for turtle in turtle_model:
        turtle_set(*turtle)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glDisableVertexAttribArray(vertex_attr)

pyglet.app.run()

uniform vec2 scale;
uniform vec4 turtle;
uniform vec2 size;

attribute vec4 vertex;

void main()
{
    float x = size.x / scale.x;
    float y = size.y / scale.y;
    mat4 model = mat4(
        turtle.z * x, -turtle.w * y,  0.0, turtle.x / scale.x,
        turtle.w * x,  turtle.z * y,  0.0, turtle.y / scale.y,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
    gl_Position = vertex * model;
}

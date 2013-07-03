uniform vec2 scale;
attribute vec4 vertex;
attribute vec4 turtle;

void main()
{
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
}

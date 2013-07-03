uniform vec2 scale;
attribute vec2 shape_vertex;
attribute vec4 turtle;

void main()
{
    // currently vertex is just 2d data
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
}

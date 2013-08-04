uniform vec2 world_scale;
uniform float geometry_scale;

attribute vec4 vertex;
attribute vec4 turtle1; // x, y, scale x, scale y
attribute vec4 turtle2; // degrees, speed, cos, sin
attribute vec4 turtle_fill_color; // rgba

varying vec4 out_turtle_color;

void main()
{
    float scale_x = turtle1.z / world_scale.x * geometry_scale;
    float scale_y = turtle1.w / world_scale.y * geometry_scale;
    float ct = turtle2.z;
    float st = turtle2.w;
    // hand-rolled 2d scale, transform, and rotate in z axis matrix
    mat4 model = mat4(
        ct * scale_x, -st * scale_y,  0.0, turtle1.x / world_scale.x,
        st * scale_x,  ct * scale_y,  0.0, turtle1.y / world_scale.y,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
    vec4 world_vertex = vertex * model;
    gl_Position = world_vertex;
    out_turtle_color = turtle_fill_color;
}

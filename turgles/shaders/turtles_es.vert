uniform float world_scale;
//uniform float geometry_scale;
uniform mat4 projection;
uniform mat4 view;
uniform vec4 turtle1; // x, y, scale x, scale y
uniform vec4 turtle2; // degrees, speed, cos, sin
uniform vec4 turtle_fill_color; // rgba

attribute vec4 vertex;

varying vec4 out_turtle_color;

void main()
{
    float scale_x = turtle1.z / world_scale;
    float scale_y = turtle1.w / world_scale;
    float ct = turtle2.z;
    float st = turtle2.w;
    // hand-rolled 2d scale/transform/rotate in row-major format
    mat4 model = transpose(mat4(
        ct * scale_x, -st * scale_y,  0.0, turtle1.x / world_scale,
        st * scale_x,  ct * scale_y,  0.0, turtle1.y / world_scale,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    ));
    mat4 transform = projection * view * model;
    vec4 world_vertex = transform * vertex;
    gl_Position = world_vertex;
    out_turtle_color = turtle_fill_color;
}

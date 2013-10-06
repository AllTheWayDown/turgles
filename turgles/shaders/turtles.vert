#version 120
uniform float world_scale;
uniform mat4 projection;
uniform mat4 view;

// instanced turtle data
attribute mat4 turtle_model;
attribute mat3 turtle_color;

attribute vec4 vertex;
attribute vec3 edge;

varying vec4 out_fill_color;
varying vec4 out_border_color;
varying float out_border_thickness;
varying vec3 out_edge;

void main()
{
    float x = turtle_model[0][0];
    float y = turtle_model[0][1];
    float scale_x = turtle_model[0][2] / world_scale;
    float scale_y = turtle_model[0][3] / world_scale;
    float ct = turtle_model[1][2];
    float st = turtle_model[1][3];

    // hand-rolled 2d scale/transform/rotate in row-major format
    mat4 model = transpose(mat4(
        ct * scale_x, -st * scale_y,  0.0, x / world_scale,
        st * scale_x,  ct * scale_y,  0.0, y / world_scale,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    ));
    mat4 transform = projection * view * model;
    vec4 world_vertex = transform * vertex;
    gl_Position = world_vertex;
    
    out_border_color = vec4(
        turtle_color[0][0],
        turtle_color[0][1],
        turtle_color[0][2],
        turtle_color[1][0]
    );
    out_fill_color =  vec4(
        turtle_color[1][1],
        turtle_color[1][2],
        turtle_color[2][0],
        turtle_color[2][1]
    );
    out_border_thickness = turtle_color[2][2];
    out_edge = edge; // * world_vertex.w * z;
}

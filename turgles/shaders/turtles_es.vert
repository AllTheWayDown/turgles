#version 120
// default array size assumes 4096 uniform locations
//
// Calculated as follows
// ARRAY_SIZE = (GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB - STATIC_UNIFORMS) // ARRAY_UNIFORMS
// where STATIC_UNIFORMS is the memory cost of normal uniforms, currentlt 16 + 16 + 1
// and ARRAY_UNIFORMS is memory costs of all array members, currently 16 + 12
//
#ifndef ARRAY_SIZE
#define ARRAY_SIZE 145
#endif

uniform float world_scale;  // cost 16
uniform mat4 projection;    // cost 16
uniform mat4 view;          // cost 1

uniform mat4 turtle_model_array[ARRAY_SIZE];  // cost 16 * ARRAY_SIZE
uniform mat3 turtle_color_array[ARRAY_SIZE];  // cost 12 * ARRAY_SIZE (as have to allocate in 4s)

attribute vec4 vertex;
attribute vec3 edge;
attribute float index;

varying vec4 out_fill_color;
varying vec4 out_border_color;
varying float out_border_thickness;
varying vec3 out_edge;

void main()
{
    int i = int(index);
    mat4 turtle_model = turtle_model_array[i];
    mat3 turtle_color = turtle_color_array[i];
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

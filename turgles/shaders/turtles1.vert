uniform vec2 scale;
attribute vec4 vertex;

attribute vec4 turtle1; // x, y, scale x, scale y
attribute vec4 turtle2; // degrees, speed, cos, sin

void main()
{
    float scale_x = turtle1.z / scale.x;
    float scale_y = turtle1.w / scale.y;
    float ct = turtle2.z;
    float st = turtle2.w;
    mat4 model = mat4(
        ct * scale_x, -st * scale_y,  0.0, turtle1.x / scale.x,
        st * scale_x,  ct * scale_y,  0.0, turtle1.y / scale.y,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
    gl_Position = vertex * model;
}

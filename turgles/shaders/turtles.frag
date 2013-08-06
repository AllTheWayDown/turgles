varying vec4 out_turtle_color;
varying vec3 out_edge;


#extension GL_OES_standard_derivatives : enable
float edgeFactor()
{
    vec3 d = fwidth(out_edge);
    vec3 a3 = smoothstep(vec3(0.0), d*0.95, out_edge);
    return min(min(a3.x, a3.y), a3.z);
}

void main()
{
    float edge_dist = min(min(out_edge.x, out_edge.y), out_edge.z);
    if (edge_dist < 0.15)
        gl_FragColor = vec4(0, 0, 0, 1);
    else
        gl_FragColor = out_turtle_color;
}

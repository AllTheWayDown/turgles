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
    float I = exp2(-2.0 * edge_dist * edge_dist);
    gl_FragColor.rgb = I * vec3(0,0,0) + (1.0 - I) * out_turtle_color;
    gl_FragColor.a = 1.0;
}

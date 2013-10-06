varying vec4 out_fill_color;
varying vec4 out_border_color;
varying float out_border_thickness;
varying vec3 out_edge;

void main()
{
    float edge_dist = min(min(out_edge.x, out_edge.y), out_edge.z);
    if (edge_dist <= out_border_thickness)
        gl_FragColor = out_border_color;
    else
        gl_FragColor = out_fill_color;
    //float I = exp2(-0.1 * edge_dist * edge_dist * edge_dist);
    //gl_FragColor.rgb = I * vec3(0,0,0) + (1.0 - I) * out_turtle_color;
    //gl_FragColor.a = 1.0;
}

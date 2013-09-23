varying vec4 out_turtle_color;
varying vec3 out_edge;

void main()
{
    vec4 border = vec4(0, 0, 0, 1);
    float edge_dist = min(min(out_edge.x, out_edge.y), out_edge.z);
    if (edge_dist <= 0.5)
        gl_FragColor = border;
    else
        gl_FragColor = out_turtle_color;
    //float I = exp2(-0.1 * edge_dist * edge_dist * edge_dist);
    //gl_FragColor.rgb = I * vec3(0,0,0) + (1.0 - I) * out_turtle_color;
    //gl_FragColor.a = 1.0;
}

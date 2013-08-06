varying vec4 out_turtle_color;
varying vec3 out_edge;


#extension GL_OES_standard_derivatives : enable
float edgeFactor()
{
    vec3 d = fwidth(out_edge);
    vec3 a3 = smoothstep(vec3(0.0), d*1, out_edge);
    return min(min(a3.x, a3.y), a3.z);
}

void main()
{
    gl_FragColor.rgb = mix(vec3(0.0), out_turtle_color.rgb, edgeFactor());
    gl_FragColor.a = 1.0;
}

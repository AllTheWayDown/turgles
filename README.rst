TurGLES
=======

OpenGL ES backend for rendering turtles

Status: experimenting, pre-alpha

Hard Goals:
 - Fast renderer for a turtle-like world
 - RasPi compatible
 - Full 3d camera
 - Custom 3D turle geometry
 - Scales to 10,000 turtles
 - Texture mapping images as turtle

Stretch Goals:
 - Drop in replacement renderer for stdlib turtle module\*
 - Use shaders to simulate turtle world, not just render
 - Extensible (custom turtle shaders, new world objects)

\* via monkey patching, as turtle module not easily extensible


Development
===========

    virtualenv turgles
    pip install -r requirements.txt


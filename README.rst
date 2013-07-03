turgles
=======

OpenGL ES backend for python turtle module

Status: experimenting, pre-pre-pre alpha

Goals:
 1. Drop in\* renderer for stdlib turtle module
 2. RaspPi compatible
 3. Full 3d camera
 4. Custom 3D turle geometry, w/texture mapping
 5. Extensible (custom turtle shaders, new world objects)
 6. Provide custom turtle class that does *all* maths in the shaders


\* probably via monkey patching, as turtle module is only partially extensible


Development
===========


    virtualenv -p python3.2 turgles
    pip install -r requirements.txt


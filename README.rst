TurGLES
=======

An OpenGL backend for rendering turtles. Designed to be used as backend for
NinjaTurtle_.


Status: experimenting, pre-alpha

Features:

 * Fast renderer for a turtle-like world
 * Two OpenGL render methods: ES2.0 compatible for older hardware/drivers, and
   a faster ES3.0 compatible method for modern OpenGL
 * Simple 3d camera
 * Scales to 10,000 turtles at 60fps (the t10k problem :)

Limitations:

 * Does not yet support drawing pen lines/trails, or stamping.
 * Borders on the most complex "turtle" shape are a bit, erm, funky.
 * Cannot easily create custom shapes

Planned features:

 * RasPi compatible (need EGL support, requires moving away from pyglet)
 * Texture mapping images as turtle
 * Full 3d camera
 * Custom 3D turle geometry

Possible features:

 * Drop in replacement renderer for stdlib turtle module\*
 * Use GPU to simulate turtle world, not just render (via Transform Feedback)

\* via monkey patching, as turtle module not easily extensible


Overview
--------

Use pyglet 1.2 alpha (for python 3) to provide GL context, GL api, and windowing.
This will change at some point, as it doesn't look like there will be a release
of 1.2 any time soon. Plus, I'd prefer to move to cffi-based OpenGL wrapper.
Plus, no EGL support. Plus don't use 90% of it. Plus not on PyPI. You get the drift.

ES2 rendering method uses pseudo-instancing (using uniform arrays and mutliple
copies of vertices), and should work on any card supporting ES2 or OpenGL 3.0,
possibly even 2.1 with the right extensions.

The ES3 method uses hardware instancing (glDrawArraysInstanced and
glVertexAttribDivisor), as well as VAOs. It's about 10-20x faster.

Both methods use vertex arrays with per-vertex barycentric coordinate metadata
for drawing borders in one pass (see geometry.py for more info and references).

Data is stored in 2 cffi-created float arrays per turtle shape, one for
position data, one for color data. The reason for 2 arrays are a) minimise
shared data layout with NinjaTurtle and b) simplifies ES2/ES3 renderer
differences, due to maximum uniform size being 16 floats.

Shader wise, very simple manually calculated transform is used. Only difference
between ES2/3 shader is how the model data is communicated (uniform in ES2,
attribute in ES3). The fragment shader is identical for both ES2/3 methods.

Installation
------------

You will require a C compiler, currently. For Mac OSX, usually with the XCode
Command Line Tools.

Install into a virtualenv for best results.

.. code::

    pip install -r requirements.txt

Tests
-----

.. code::

    python setup.py test

If you have tox installed you can run tests against 2.7, 3.3, and pypy

.. code::

    tox

Demo
----

Standalone, turgles doesn't do much. But there's a demo that can be run.

.. code::

    cd turgles
    python demo.py

For a better benchmark, use compile the c helper for animating the turtles in
a random walk, so you are stressing the CPU less.

.. code::

    make

.. _NinjaTurtle: http://www.github.com/AllTheWayDown/ninjaturtle

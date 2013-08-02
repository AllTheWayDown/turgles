import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="turgles",
    version="0.1",
    author="Simon Davy",
    author_email="bloodearnest@gmail.com",
    description=("An OpenGL ES renderer for LOGO style turtles."),
    license="MIT",
    keywords="turtle education kids opengl",
    url="https://github.com/AllTheWayDown/turgles",
    packages=find_packages(exclude=['tests']),
    package_dir={'turgles': 'turgles'},
    package_data={'turgles': ['shaders/*.vert', 'shaders/*.frag']},
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Education",
        "Topic :: Games/Entertainment :: Simulation",
    ],
    test_suite='turgles.tests',
    install_requires=[
        'cffi==0.7',
        'pycparser==2.09.1',
        'pyglet==1.2alpha1',
    ],
)

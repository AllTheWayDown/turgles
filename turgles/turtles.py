from random import randint, random, expovariate
from math import radians, sin, cos, pi


class Turtle(object):

    def __init__(self, n, data)
        self.data = data
        self.x = data[n * 



def random_walk(turtle, mean, angle):
    x = t * turtle_data_size
    y = x + 1
    angle = x + 2

    turtle_model[angle] += expovariate(lambd) - degrees
    theta = radians(turtle_model[angle])
    dy = magnitude * sin(theta)
    dx = magnitude * cos(theta)
    turtle_model[x] += dx
    turtle_model[y] += dy
    if turtle_model[x] > half_size:
        turtle_model[x] -= world_size
    elif turtle_model[x] < -half_size:
        turtle_model[x] += world_size
    if turtle_model[y] > half_size:
        turtle_model[y] -= world_size
    elif turtle_model[y] < -half_size:
        turtle_model[y] += world_size

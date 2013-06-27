import array
from time import time


class TurtleView():
    """Per instance offsets and array reference"""
    __slots__ = ('_turtles', 'X', 'Y', 'ANGLE', 'SIZE')

    def __init__(self, turtles, num):
        self._turtles = turtles
        self.X, self.Y, self.ANGLE, self.SIZE = (num + i for i in range(4))

    def getx(self):
        return self._turtles[self.X]
    def setx(self, x):
        self._turtles[self.X] = x
    x = property(getx, setx)

    def gety(self):
        return self._turtles[self.Y]
    def sety(self, y):
        self._turtles[self.Y] = y
    y = property(gety, sety)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

TURTLES = None

class TurtleView2():
    """Global array reference and per instance offsets."""
    __slots__ = ('X', 'Y', 'ANGLE', 'SIZE')

    def __init__(self, _, num):
        self.X, self.Y, self.ANGLE, self.SIZE = (num + i for i in range(4))

    def getx(self):
        return TURTLES[self.X]
    def setx(self, x):
        TURTLES[self.X] = x

    x = property(getx, setx)

    def gety(self):
        return TURTLES[self.Y]
    def sety(self, y):
        TURTLES[self.Y] = y
    y = property(gety, sety)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


class TurtleView3():
    """Constant offsets and memoryview. 3.3 only"""
    __slots__ = ('view')

    def __init__(self, turtles, num):
        self.view = memoryview(turtles)[num:num + 4]

    def getx(self):
        return self.view[0]
    def setx(self, x):
        self.view[0] = x

    x = property(getx, setx)

    def gety(self):
        return self.view[1]
    def sety(self, y):
        self.view[1] = y
    y = property(gety, sety)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


num_turtles = 10000
TURTLES = array.array("f", range(num_turtles * 4))


def bench(f):
    objs = [f(TURTLES, i * 4) for i in range(num_turtles)]
    start = time()
    for t in objs:
        t.x += 1
        t.y += 1
    return time() - start

def direct():
    t = turtles
    x = range(num_turtles)
    start = time()
    for i in x:
        n = i * 4
        t[n] += 1
        t[n + 1] += 1
    return time() - start


turtles = array.array("f", range(num_turtles * 4))
print(bench(TurtleView))
turtles = array.array("f", range(num_turtles * 4))
print(bench(TurtleView2))
turtles = array.array("f", range(num_turtles * 4))
print(bench(TurtleView3))
turtles = array.array("f", range(num_turtles * 4))
print(direct())







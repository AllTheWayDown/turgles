from __future__ import division, print_function, absolute_import

from turgles.memory import create_turtle_buffer, TURTLE_DATA_SIZE


class TurtleBuffer(object):
    """A managed buffer of turtle data"""

    class Full(Exception):
        pass

    def __init__(self, shape, size):
        self.shape = shape
        self.size = size
        self.count = 0
        self.data = create_turtle_buffer(size)

    def new(self):
        if self.count >= self.size:
            raise self.Full()

        index = self.count * TURTLE_DATA_SIZE
        slice = self.data[index:index + TURTLE_DATA_SIZE]
        self.count += 1
        return slice

    def remove(self, index):
        pass

    @classmethod
    def copy(cls, old, size):
        """Creates a larger buffer, copying in the old buffer's data"""
        assert size > old.size
        new = cls(old.shape, size)
        new.data[0:old.size * TURTLE_DATA_SIZE] = old.data
        new.count = size
        return new

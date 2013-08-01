from __future__ import division, print_function, absolute_import
from itertools import count

from turgles.memory import create_turtle_buffer, TURTLE_DATA_SIZE

TURTLE_ID = count()

ID_TO_INDEX = {}
INDEX_TO_ID = {}


class TurtleBuffer(object):
    """A managed buffer of turtle data"""

    class Full(Exception):
        pass

    def __init__(self, shape, size):
        self.shape = shape
        self.size = size
        self.count = 0
        self.data = create_turtle_buffer(size)
        self.id_to_index = {}
        self.index_to_id = {}

    def _get_data(self, index):
        assert index <= self.count
        assert index < self.size
        offset = index * TURTLE_DATA_SIZE
        return self.data[offset:offset + TURTLE_DATA_SIZE]

    def _update_id_map(self, id, index):
        self.id_to_index[id] = index
        self.index_to_id[index] = id

    def new(self, init=None):
        if self.count >= self.size:
            raise self.Full()
        if init is not None:
            assert len(init) == TURTLE_DATA_SIZE

        id = next(TURTLE_ID)
        data = self._get_data(self.count)
        self._update_id_map(id, self.count)

        self.count += 1
        if init is not None:
            data[0:TURTLE_DATA_SIZE] = init

        return id, data

    def remove(self, id):
        remove_index = self.id_to_index[id]
        last_index = self.count - 1
        remove_data = self._get_data(remove_index)

        if remove_index == last_index:
            # easy - nothing to do
            last_data = remove_data
        else:
            last_data = self._get_data(last_index)
            # copy the last turtle's data over data to be deleted
            remove_data[0:TURTLE_DATA_SIZE] = last_data
            # update id map for the last turtle to new location
            last_id = self.index_to_id[last_index]
            self._update_id_map(last_id, remove_index)

        # zero last turtle's data
        last_data[0:TURTLE_DATA_SIZE] = [0] * TURTLE_DATA_SIZE
        del self.index_to_id[last_index]
        del self.id_to_index[id]
        self.count -= 1

    @classmethod
    def copy(cls, old, size):
        """Creates a larger buffer, copying in the old buffer's data"""
        assert size > old.size
        new = cls(old.shape, size)
        new.data[0:old.size * TURTLE_DATA_SIZE] = old.data
        new.count = old.count
        return new

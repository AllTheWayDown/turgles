from __future__ import division, print_function, absolute_import
import itertools
import logging
log = logging.getLogger('turgles')

from turgles.memory import create_turtle_buffer, TURTLE_DATA_SIZE


class TurtleBuffer(object):
    """A managed buffer of turtle data"""

    def __init__(self, shape, size):
        self.shape = shape
        self.size = size
        self.count = 0
        self.data = create_turtle_buffer(self.size)
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

    def get(self, id):
        return self._get_data(self.id_to_index[id])

    def new(self, id, init=None):
        assert id not in self.id_to_index
        if init is not None:
            assert len(init) == TURTLE_DATA_SIZE
        if self.count >= self.size:
            self._resize()

        data = self._get_data(self.count)
        self._update_id_map(id, self.count)

        self.count += 1
        if init is not None:
            data[0:TURTLE_DATA_SIZE] = init

        return data

    def _resize(self):
        """Creates a larger buffer, copying in the old buffer's data"""
        log.debug(
            "resizing turtle buffer from {} to {} for shape {}".format(
                self.size, self.size * 2, self.shape)
        )
        new_data = create_turtle_buffer(self.size * 2)
        new_data[0:self.size * TURTLE_DATA_SIZE] = self.data
        self.size *= 2
        self.data = new_data

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


class BufferManager(object):

    TURTLE_ID = itertools.count()

    def __init__(self, size):
        self.size = size
        self.buffers = {}
        self.id_to_shape = {}

    def get_id(self):
        return next(self.TURTLE_ID)

    def get_buffer(self, shape):
        if shape in self.buffers:
            return self.buffers[shape]

        buffer = TurtleBuffer(shape, self.size)
        self.buffers[shape] = buffer
        return buffer

    def create_turtle(self, shape, init=None):
        """Public api to ninjaturtle"""
        id = self.get_id()
        data = self._create_turtle(shape, id, init)
        self.id_to_shape[id] = shape
        return id, data

    def _create_turtle(self, shape, id, init=None):
        buffer = self.get_buffer(shape)
        data = buffer.new(id, init)
        return data

    def set_shape(self, id, new_shape):
        """Copies the turtle data from the old shape buffer to the new"""
        old_shape = self.id_to_shape[id]
        old_buffer = self.get_buffer(old_shape)
        data = old_buffer.get(id)
        new_data = self._create_turtle(new_shape, id, data)
        old_buffer.remove(id)
        return new_data

    def destroy_turtle(self, id):
        shape = self.id_to_shape[id]
        buffer = self.get_buffer(shape)
        buffer.remove(id)
        del self.id_to_shape[id]

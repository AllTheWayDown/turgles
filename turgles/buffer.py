from __future__ import division, print_function, absolute_import
import logging
log = logging.getLogger('turgles')

from turgles.memory import (
    ffi,
    sizeof,
    TURTLE_MODEL_DATA_SIZE,
    TURTLE_COLOR_DATA_SIZE,
)


class ChunkBuffer(object):
    """A resizable cffi-based buffer that provides data indexed in chunks"""

    def __init__(self, size, chunk_size, ctype='float'):
        """Create a new buffer of n chunks.

        Parameters:
            size: number of chunks
            chunk_size: size of each chunk
            ctype: string of the C type to use (defaults to float)
        """
        self.count = 0                # current number of chunks
        self.size = size              # max number of chunks
        self.chunk_size = chunk_size  # size of chunks
        self.ctype = ctype
        self.data = self._allocate(size)
        self.ctype_size = sizeof(self.data[0:1])

    def _allocate(self, size):
        return ffi.new('{}[{}]'.format(self.ctype, size * self.chunk_size))

    @property
    def byte_size(self):
        return self.count * self.chunk_size * self.ctype_size

    def __iter__(self):
        """Iterates over chunks"""
        chunk_size = self.chunk_size
        for i in range(self.count):
            offset = i * chunk_size
            yield self.data[offset:offset + chunk_size]

    def get(self, index):
        """Get a chunk by index"""
        assert index <= self.count
        assert index < self.size
        offset = index * self.chunk_size
        return self.data[offset:offset + self.chunk_size]

    def new(self, init=None):
        """Return the last currently unused chunk, resizing if needed.

        If init is passed, chunk will be initialised to that data"""
        if self.count >= self.size:
            self.resize(self.count * 2)
        chunk = self.get(self.count)
        if init is not None:
            assert len(init) == self.chunk_size
            chunk[0:self.chunk_size] = init
        self.count += 1
        return chunk

    def resize(self, new_size):
        """Create a new larger array, and copy data over"""
        assert new_size > self.size
        new_data = self._allocate(new_size)
        # copy
        new_data[0:self.size * self.chunk_size] = self.data
        self.size = new_size
        self.data = new_data

    def remove(self, index):
        """Remove chunk at index.

        Doesn't actually delete data, copies last chunk's data over data to be
        removed, and decreases the count"""
        assert index < self.count
        last_index = self.count - 1
        data = self.get(index)

        if index == last_index:
            # easy case - nothing to do except zero last chunk
            last_data = data
            moved = None
        else:
            last_data = self.get(last_index)
            # copy the last chunk's data over the data to be deleted
            data[0:self.chunk_size] = last_data
            moved = last_index

        # zero last chunk's data
        last_data[0:self.chunk_size] = [0] * self.chunk_size
        self.count -= 1

        # provide which index has now moved
        return moved


class ShapeBuffer(object):
    """A pair of chunked buffers of data.

    One is the model buffer, layed out like NinjaTurtle. The other is the color
    buffer, which is just used in Turgles
    """

    def __init__(self, shape, size):
        self.shape = shape
        self.model = ChunkBuffer(size, TURTLE_MODEL_DATA_SIZE)
        self.color = ChunkBuffer(size, TURTLE_COLOR_DATA_SIZE)
        self.id_to_index = {}
        self.index_to_id = {}

    @property
    def count(self):
        count = self.model.count
        assert count == self.color.count
        return count

    @property
    def size(self):
        size = self.model.size
        assert size == self.color.size
        return size

    def __iter__(self):
        for model, color in zip(self.model, self.color):
            yield model, color

    def _update_id_map(self, id, index):
        self.id_to_index[id] = index
        self.index_to_id[index] = id

    def get_model(self, id):
        return self.model.get(self.id_to_index[id])

    def get_color(self, id):
        return self.color.get(self.id_to_index[id])

    def get(self, id):
        index = self.id_to_index[id]
        return self.model.get(index), self.color.get(index)

    def new(self, id, model_init=None, color_init=None):
        assert id not in self.id_to_index

        # cache the current count
        count = self.model.count
        model_data = self.model.new(model_init)
        color_data = self.color.new(color_init)
        self._update_id_map(id, count)

        return model_data, color_data

    def remove(self, id):
        index = self.id_to_index[id]

        moved_model_index = self.model.remove(index)
        moved_color_index = self.color.remove(index)
        assert moved_model_index == moved_color_index
        if moved_model_index:
            # update id map for the last turtle to new location
            moved_id = self.index_to_id[moved_model_index]
            self._update_id_map(moved_id, index)
            del self.index_to_id[moved_model_index]
        else:
            del self.index_to_id[index]
        del self.id_to_index[id]


class BufferManager(object):

    def __init__(self, size):
        self.size = size
        self.buffers = {}
        self.id_to_shape = {}

    def get_buffer(self, shape):
        if shape in self.buffers:
            return self.buffers[shape]

        buffer = ShapeBuffer(shape, self.size)
        self.buffers[shape] = buffer
        return buffer

    def create_turtle(self, id, shape, model_init, color_init):
        """Create a slice of memory for turtle data storage"""
        assert id not in self.id_to_shape
        data = self._create_turtle(id, shape, model_init, color_init)
        self.id_to_shape[id] = shape
        return data

    def _create_turtle(self, id, shape, model_init, color_init):
        buffer = self.get_buffer(shape)
        data = buffer.new(id, model_init, color_init)
        return data

    def set_shape(self, id, new_shape):
        """Copies the turtle data from the old shape buffer to the new"""
        old_shape = self.id_to_shape[id]
        old_buffer = self.get_buffer(old_shape)
        model, color = old_buffer.get(id)
        new_data = self._create_turtle(id, new_shape, model, color)
        old_buffer.remove(id)
        self.id_to_shape[id] = new_shape
        return new_data

    def destroy_turtle(self, id):
        shape = self.id_to_shape[id]
        buffer = self.get_buffer(shape)
        buffer.remove(id)
        del self.id_to_shape[id]

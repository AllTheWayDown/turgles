import itertools
from unittest import TestCase

from turgles.buffer import ChunkBuffer, ShapeBuffer, BufferManager
from turgles.memory import TURTLE_MODEL_DATA_SIZE, TURTLE_COLOR_DATA_SIZE

MODEL_ZEROS = [0] * TURTLE_MODEL_DATA_SIZE
MODEL_ONES = [1] * TURTLE_MODEL_DATA_SIZE
MODEL_TWOS = [2] * TURTLE_MODEL_DATA_SIZE
MODEL_THREES = [3] * TURTLE_MODEL_DATA_SIZE

COLOR_ZEROS = [0] * TURTLE_COLOR_DATA_SIZE
COLOR_ONES = [1] * TURTLE_COLOR_DATA_SIZE
COLOR_TWOS = [2] * TURTLE_COLOR_DATA_SIZE
COLOR_THREES = [3] * TURTLE_COLOR_DATA_SIZE


class ChunkBufferTestCase(TestCase):

    def assert_turtle_data(self, buffer, index, data):
        offset = index * TURTLE_MODEL_DATA_SIZE
        slice = buffer.data[offset:offset + TURTLE_MODEL_DATA_SIZE]
        self.assertEqual(list(slice), data)

    def test_sized_correctly(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        self.assertEqual(len(buffer.data), 4 * TURTLE_MODEL_DATA_SIZE)
        self.assertEqual(buffer.count, 0)
        self.assertEqual(buffer.size, 4)

    def test_new(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        data = buffer.new()
        self.assertEqual(len(data), TURTLE_MODEL_DATA_SIZE)
        self.assertEqual(list(data), MODEL_ZEROS)
        self.assertEqual(buffer.count, 1)

    def test_new_with_init(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        init = list(reversed(range(TURTLE_MODEL_DATA_SIZE)))
        data = buffer.new(init)
        self.assertEqual(len(data), TURTLE_MODEL_DATA_SIZE)
        self.assertEqual(list(data), init)

    def test_mutlple_new(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        buffer.new()
        self.assertEqual(buffer.count, 1)
        buffer.new()
        self.assertEqual(buffer.count, 2)

    def test_new_triggers_resize(self):
        buffer = ChunkBuffer(2, TURTLE_MODEL_DATA_SIZE)
        buffer.new()
        buffer.new()
        self.assertEqual(buffer.size, 2)
        self.assertEqual(buffer.count, 2)
        buffer.new()
        self.assertEqual(buffer.size, 4)
        self.assertEqual(buffer.count, 3)

    def test_resize(self):
        buffer = ChunkBuffer(2, TURTLE_MODEL_DATA_SIZE)
        buffer.new(MODEL_ONES)
        buffer.new(MODEL_TWOS)
        buffer.resize(4)
        self.assertEqual(buffer.size, 4)
        self.assertEqual(len(buffer.data), 4 * TURTLE_MODEL_DATA_SIZE)
        self.assert_turtle_data(buffer, 0, MODEL_ONES)
        self.assert_turtle_data(buffer, 1, MODEL_TWOS)
        self.assert_turtle_data(buffer, 2, MODEL_ZEROS)
        self.assert_turtle_data(buffer, 3, MODEL_ZEROS)

    def test_remove_end(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        buffer.new(MODEL_ONES)
        buffer.new(MODEL_TWOS)
        buffer.new(MODEL_THREES)
        moved = buffer.remove(2)
        self.assertEqual(buffer.count, 2)
        self.assertIsNone(moved)
        self.assert_turtle_data(buffer, 0, MODEL_ONES)
        self.assert_turtle_data(buffer, 1, MODEL_TWOS)
        self.assert_turtle_data(buffer, 2, MODEL_ZEROS)

    def test_remove_start(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        buffer.new(MODEL_ONES)
        buffer.new(MODEL_TWOS)
        buffer.new(MODEL_THREES)
        moved = buffer.remove(0)
        self.assertEqual(buffer.count, 2)
        self.assertEqual(moved, 2)
        self.assert_turtle_data(buffer, 0, MODEL_THREES)
        self.assert_turtle_data(buffer, 1, MODEL_TWOS)
        self.assert_turtle_data(buffer, 2, MODEL_ZEROS)

    def test_remove_middle(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        buffer.new(MODEL_ONES)
        buffer.new(MODEL_TWOS)
        buffer.new(MODEL_THREES)
        moved = buffer.remove(1)
        self.assertEqual(buffer.count, 2)
        self.assertEqual(moved, 2)
        self.assert_turtle_data(buffer, 0, MODEL_ONES)
        self.assert_turtle_data(buffer, 1, MODEL_THREES)
        self.assert_turtle_data(buffer, 2, MODEL_ZEROS)

    def test_remove_then_add(self):
        buffer = ChunkBuffer(4, TURTLE_MODEL_DATA_SIZE)
        buffer.new(MODEL_ONES)
        buffer.new(MODEL_TWOS)
        buffer.new(MODEL_THREES)
        buffer.remove(2)
        self.assertEqual(buffer.count, 2)
        # check data was zeroed
        self.assert_turtle_data(buffer, 2, MODEL_ZEROS)

        buffer.new([4] * TURTLE_MODEL_DATA_SIZE)
        self.assertEqual(buffer.count, 3)
        # check reuses previously removed turtle's space
        self.assert_turtle_data(buffer, 2, [4] * TURTLE_MODEL_DATA_SIZE)

    def make_slices(self, size, array_size=20):
        buffer = ChunkBuffer(array_size, TURTLE_MODEL_DATA_SIZE)
        for i in range(array_size):
            buffer.new([i+1] * TURTLE_MODEL_DATA_SIZE)

        return buffer.slice(size)

    def test_slice_size_multiple(self):
        slices = self.make_slices(10, 20)
        size, slice = next(slices)
        self.assertEqual(size, 10)
        self.assertEqual(
            list(slice[0:TURTLE_MODEL_DATA_SIZE]),
            [1] * TURTLE_MODEL_DATA_SIZE
        )
        size, slice = next(slices)
        self.assertEqual(size, 10)
        self.assertEqual(
            list(slice[0:TURTLE_MODEL_DATA_SIZE]),
            [11] * TURTLE_MODEL_DATA_SIZE
        )
        with self.assertRaises(StopIteration):
            next(slices)

    def test_slice_size_remainder(self):
        slices = self.make_slices(15, 20)
        size, slice = next(slices)
        self.assertEqual(size, 15)
        self.assertEqual(
            list(slice[0:TURTLE_MODEL_DATA_SIZE]),
            [1] * TURTLE_MODEL_DATA_SIZE
        )
        size, slice = next(slices)
        self.assertEqual(size, 5)
        self.assertEqual(
            list(slice[0:TURTLE_MODEL_DATA_SIZE]),
            [16] * TURTLE_MODEL_DATA_SIZE
        )
        with self.assertRaises(StopIteration):
            next(slices)

    def test_slice_size_only_one(self):
        slices = self.make_slices(20, 10)
        size, slice = next(slices)
        self.assertEqual(size, 10)
        self.assertEqual(
            list(slice[0:TURTLE_MODEL_DATA_SIZE]),
            [1] * TURTLE_MODEL_DATA_SIZE
        )
        with self.assertRaises(StopIteration):
            next(slices)




class ShapeBufferTestCase(TestCase):

    def assert_id_map(self, buffer, id, index):
        self.assertIn(id, buffer.id_to_index)
        self.assertIn(index, buffer.index_to_id)
        self.assertEqual(buffer.id_to_index[id], index)
        self.assertEqual(buffer.index_to_id[index], id)

    def assert_turtle_data(self, buffer, id, index, model, color):
        if id:
            self.assert_id_map(buffer, id, index)
        model_data = buffer.model.get(index)
        color_data = buffer.color.get(index)
        self.assertEqual(list(model_data), model)
        self.assertEqual(list(color_data), color)

    def test_new(self):
        buffer = ShapeBuffer('shape', 4)
        model, color = buffer.new(0)
        self.assert_turtle_data(buffer, 0, 0, MODEL_ZEROS, COLOR_ZEROS)
        self.assertEqual(buffer.count, 1)

    def test_new_bad_id(self):
        buffer = ShapeBuffer('shape', 4)
        buffer.new(0)
        with self.assertRaises(AssertionError):
            buffer.new(0)

    def test_new_with_init(self):
        buffer = ShapeBuffer('shape', 4)
        model, color = buffer.new(0, MODEL_ONES, COLOR_TWOS)
        self.assert_turtle_data(buffer, 0, 0, MODEL_ONES, COLOR_TWOS)

    def test_mutlple_new(self):
        buffer = ShapeBuffer('shape', 4)
        buffer.new(0)
        self.assert_id_map(buffer, 0, 0)
        self.assertEqual(buffer.count, 1)
        buffer.new(1)
        self.assert_id_map(buffer, 1, 1)
        self.assertEqual(buffer.count, 2)

    def test_remove_id_end(self):
        buffer = ShapeBuffer('shape', 4)
        buffer.new(0, MODEL_ONES, COLOR_ONES)
        buffer.new(1, MODEL_TWOS, COLOR_TWOS)
        buffer.new(2, MODEL_THREES, COLOR_THREES)
        self.assert_turtle_data(buffer, 2, 2, MODEL_THREES, COLOR_THREES)
        buffer.remove(2)
        self.assertEqual(buffer.count, 2)
        self.assert_turtle_data(buffer, 0, 0, MODEL_ONES, COLOR_ONES)
        self.assert_turtle_data(buffer, 1, 1, MODEL_TWOS, COLOR_TWOS)
        # check last one zeroed
        self.assert_turtle_data(buffer, None, 2, MODEL_ZEROS, COLOR_ZEROS)
        self.assertNotIn(2, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)

    def test_remove_id_start(self):
        buffer = ShapeBuffer('shape', 4)
        buffer.new(0, MODEL_ONES, COLOR_ONES)
        buffer.new(1, MODEL_TWOS, COLOR_TWOS)
        buffer.new(2, MODEL_THREES, COLOR_THREES)
        self.assert_turtle_data(buffer, 0, 0, MODEL_ONES, COLOR_ONES)
        buffer.remove(0)
        self.assertEqual(buffer.count, 2)
        # check last one has been copied to 0
        self.assert_turtle_data(buffer, 2, 0, MODEL_THREES, COLOR_THREES)
        self.assert_turtle_data(buffer, 1, 1, MODEL_TWOS, COLOR_TWOS)
        # check last one zeroed
        self.assert_turtle_data(buffer, None, 2, MODEL_ZEROS, COLOR_ZEROS)
        self.assertNotIn(0, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)

    def test_remove_id_middle(self):
        buffer = ShapeBuffer('shape', 4)
        buffer.new(0, MODEL_ONES, COLOR_ONES)
        buffer.new(1, MODEL_TWOS, COLOR_TWOS)
        buffer.new(2, MODEL_THREES, COLOR_THREES)
        self.assert_turtle_data(buffer, 1, 1, MODEL_TWOS, COLOR_TWOS)
        buffer.remove(1)
        self.assertEqual(buffer.count, 2)
        # check last has been copied to 1
        self.assert_turtle_data(buffer, 0, 0, MODEL_ONES, COLOR_ONES)
        self.assert_turtle_data(buffer, 2, 1, MODEL_THREES, COLOR_THREES)
        # check last one zeroed
        self.assert_turtle_data(buffer, None, 2, MODEL_ZEROS, COLOR_ZEROS)
        self.assertNotIn(1, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)


class BufferManagerTestCase(TestCase):

    def test_get_buffer(self):
        manager = BufferManager(4)
        self.assertEqual(len(manager.buffers), 0)
        buffer1 = manager.get_buffer('classic')
        self.assertEqual(len(manager.buffers), 1)
        self.assertIn('classic', manager.buffers)
        self.assertEqual(buffer1.size, 4)
        buffer2 = manager.get_buffer('classic')
        self.assertEqual(len(manager.buffers), 1)
        self.assertIs(buffer1, buffer2)

    def test_create_turtle(self):
        manager = BufferManager(4)
        model, color = manager.create_turtle(
            0, 'classic', MODEL_ONES, COLOR_ONES)
        self.assertEqual(list(model), MODEL_ONES)
        self.assertEqual(list(color), COLOR_ONES)
        self.assertEqual(len(manager.buffers), 1)
        self.assertIn('classic', manager.buffers)
        self.assertEqual(manager.buffers['classic'].size, 4)

    def test_set_shape(self):
        manager = BufferManager(4)
        model, color = manager.create_turtle(
            0, 'classic', MODEL_ONES, COLOR_ONES)
        model2, color2 = manager.set_shape(0, 'turtle')
        self.assertEqual(len(manager.buffers), 2)
        self.assertIn('turtle', manager.buffers)
        self.assertEqual(list(model2), MODEL_ONES)
        self.assertEqual(list(color2), COLOR_ONES)

    def test_destroy_turtle(self):
        manager = BufferManager(4)
        model, color = manager.create_turtle(
            0, 'classic', MODEL_ONES, COLOR_ONES)
        manager.destroy_turtle(0)
        self.assertEqual(list(model), MODEL_ZEROS)
        self.assertEqual(list(color), COLOR_ZEROS)
        self.assertEqual(manager.buffers['classic'].count, 0)

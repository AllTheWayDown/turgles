import itertools
from unittest import TestCase

from turgles.buffer import TurtleBuffer, BufferManager
from turgles.memory import TURTLE_DATA_SIZE

ZEROS = [0] * TURTLE_DATA_SIZE
ONES = [1] * TURTLE_DATA_SIZE
TWOS = [2] * TURTLE_DATA_SIZE
THREES = [3] * TURTLE_DATA_SIZE


class TurtleBufferTestCase(TestCase):

    def assert_id_map(self, buffer, id, index):
        self.assertIn(id, buffer.id_to_index)
        self.assertIn(index, buffer.index_to_id)
        self.assertEqual(buffer.id_to_index[id], index)
        self.assertEqual(buffer.index_to_id[index], id)

    def assert_turtle_data(self, buffer, index, data):
        offset = index * TURTLE_DATA_SIZE
        slice = buffer.data[offset:offset + TURTLE_DATA_SIZE]
        self.assertEqual(list(slice), data)

    def test_sized_correctly(self):
        buffer = TurtleBuffer('shape', 4)
        self.assertEqual(len(buffer.data), 4 * TURTLE_DATA_SIZE)
        self.assertEqual(buffer.count, 0)
        self.assertEqual(buffer.size, 4)
        self.assertEqual(buffer.shape, 'shape')

    def test_new(self):
        buffer = TurtleBuffer('shape', 4)
        data = buffer.new(0)
        self.assert_id_map(buffer, 0, 0)
        self.assertEqual(len(data), TURTLE_DATA_SIZE)
        self.assertEqual(list(data), ZEROS)
        self.assertEqual(buffer.count, 1)

    def test_new_bad_id(self):
        buffer = TurtleBuffer('shape', 4)
        buffer.new(0)
        with self.assertRaises(AssertionError):
            buffer.new(0)

    def test_new_with_init(self):
        buffer = TurtleBuffer('shape', 4)
        init = list(reversed(range(TURTLE_DATA_SIZE)))
        data = buffer.new(0, init)
        self.assert_id_map(buffer, 0, 0)
        self.assertEqual(len(data), TURTLE_DATA_SIZE)
        self.assertEqual(list(data), init)

    def test_mutlple_new(self):
        buffer = TurtleBuffer('shape', 4)
        buffer.new(0)
        self.assert_id_map(buffer, 0, 0)
        self.assertEqual(buffer.count, 1)
        buffer.new(1)
        self.assert_id_map(buffer, 1, 1)
        self.assertEqual(buffer.count, 2)

    def test_new_triggers_resize(self):
        buffer = TurtleBuffer('shape', 2)
        buffer.new(0)
        buffer.new(1)
        self.assertEqual(buffer.size, 2)
        buffer.new(2)
        self.assertEqual(buffer.size, 4)
        self.assertEqual(buffer.count, 3)

    def test_resize(self):
        buffer = TurtleBuffer('shape', 2)
        buffer.new(1, ONES)
        buffer.new(2, TWOS)
        buffer._resize()
        self.assertEqual(buffer.size, 4)
        self.assertEqual(len(buffer.data), 4 * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 0, ONES)
        self.assert_turtle_data(buffer, 1, TWOS)
        self.assert_turtle_data(buffer, 2, ZEROS)
        self.assert_turtle_data(buffer, 3, ZEROS)

    def test_remove_end(self):
        buffer = TurtleBuffer('shape', 4)
        buffer.new(0, ONES)
        buffer.new(1, TWOS)
        buffer.new(2, THREES)
        self.assert_id_map(buffer, 2, 2)
        buffer.remove(2)
        self.assertEqual(buffer.count, 2)
        self.assert_id_map(buffer, 0, 0)
        self.assert_id_map(buffer, 1, 1)
        self.assertNotIn(2, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)
        self.assert_turtle_data(buffer, 0, ONES)
        self.assert_turtle_data(buffer, 1, TWOS)
        self.assert_turtle_data(buffer, 2, ZEROS)

    def test_remove_start(self):
        buffer = TurtleBuffer('shape', 4)
        buffer.new(0, ONES)
        buffer.new(1, TWOS)
        buffer.new(2, THREES)
        self.assert_id_map(buffer, 0, 0)
        buffer.remove(0)
        self.assertEqual(buffer.count, 2)
        self.assert_id_map(buffer, 1, 1)
        self.assert_id_map(buffer, 2, 0)
        self.assertNotIn(0, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)
        self.assert_turtle_data(buffer, 0, THREES)
        self.assert_turtle_data(buffer, 1, TWOS)
        self.assert_turtle_data(buffer, 2, ZEROS)

    def test_remove_middle(self):
        buffer = TurtleBuffer('shape', 4)
        buffer.new(0, ONES)
        buffer.new(1, TWOS)
        buffer.new(2, THREES)
        self.assert_id_map(buffer, 1, 1)
        buffer.remove(1)
        self.assertEqual(buffer.count, 2)
        self.assert_id_map(buffer, 0, 0)
        self.assert_id_map(buffer, 2, 1)
        self.assertNotIn(1, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)
        self.assert_turtle_data(buffer, 0, ONES)
        self.assert_turtle_data(buffer, 1, THREES)
        self.assert_turtle_data(buffer, 2, ZEROS)

    def test_remove_then_add(self):
        buffer = TurtleBuffer('shape', 4)
        buffer.new(0, ONES)
        buffer.new(1, TWOS)
        buffer.new(2, THREES)
        buffer.remove(2)
        self.assertEqual(buffer.count, 2)
        # check data was zeroed
        self.assert_turtle_data(buffer, 2, ZEROS)

        buffer.new(3, [4] * TURTLE_DATA_SIZE)
        self.assertEqual(buffer.count, 3)
        # check reuses previously removed turtle's space
        self.assert_turtle_data(buffer, 2, [4] * TURTLE_DATA_SIZE)


class BufferManagerTestCase(TestCase):

    def setUp(self):
        super(BufferManagerTestCase, self).setUp()
        # reset id
        BufferManager.TURTLE_ID = itertools.count()

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
        id, data = manager.create_turtle('classic')
        self.assertEqual(id, 0)
        self.assertEqual(list(data), ZEROS)
        self.assertEqual(len(manager.buffers), 1)
        self.assertIn('classic', manager.buffers)
        self.assertEqual(manager.buffers['classic'].size, 4)

    def test_set_shape(self):
        manager = BufferManager(4)
        id, data = manager.create_turtle('classic', ONES)
        self.assertEqual(list(data), ONES)
        self.assertEqual(len(manager.buffers), 1)
        self.assertIn('classic', manager.buffers)
        new_data = manager.set_shape(id, 'turtle')
        self.assertEqual(len(manager.buffers), 2)
        self.assertIn('turtle', manager.buffers)
        self.assertEqual(list(new_data), ONES)
        self.assertEqual(list(data), ZEROS)

    def test_destroy_turtle(self):
        manager = BufferManager(4)
        id, data = manager.create_turtle('classic', ONES)
        self.assertEqual(list(data), ONES)
        self.assertEqual(manager.buffers['classic'].count, 1)
        manager.destroy_turtle(id)
        self.assertEqual(list(data), ZEROS)
        self.assertEqual(manager.buffers['classic'].count, 0)

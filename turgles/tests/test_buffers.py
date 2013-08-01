from unittest import TestCase

from turgles.buffer import TurtleBuffer
from turgles.memory import TURTLE_DATA_SIZE


class TurtleBufferTestCase(TestCase):

    def assert_id_map(self, buffer, id, index):
        self.assertIn(id, buffer.id_to_index)
        self.assertIn(index, buffer.index_to_id)
        self.assertEqual(buffer.id_to_index[id], index)
        self.assertEqual(buffer.index_to_id[index], id)

    def assert_turtle_data(self, buffer, index, data):
        offset = index * TURTLE_DATA_SIZE
        slice = buffer.data[offset:offset + TURTLE_DATA_SIZE]
        self.assertEqual(list(slice[0:TURTLE_DATA_SIZE]), data)

    def test_sized_correctly(self):
        buffer = TurtleBuffer('shape', 4)
        self.assertEqual(len(buffer.data), 4 * TURTLE_DATA_SIZE)
        self.assertEqual(buffer.count, 0)
        self.assertEqual(buffer.size, 4)
        self.assertEqual(buffer.shape, 'shape')

    def test_new(self):
        buffer = TurtleBuffer('shape', 4)
        id, data = buffer.new()
        self.assert_id_map(buffer, id, 0)
        self.assertEqual(len(data), TURTLE_DATA_SIZE)
        self.assertEqual(list(data), [0] * TURTLE_DATA_SIZE)
        self.assertEqual(buffer.count, 1)

    def test_new_with_init(self):
        buffer = TurtleBuffer('shape', 4)
        init = list(reversed(range(TURTLE_DATA_SIZE)))
        id, data = buffer.new(init)
        self.assert_id_map(buffer, id, 0)
        self.assertEqual(len(data), TURTLE_DATA_SIZE)
        self.assertEqual(list(data), init)

    def test_mutlple_new(self):
        buffer = TurtleBuffer('shape', 4)
        id, data = buffer.new()
        self.assert_id_map(buffer, id, 0)
        self.assertEqual(buffer.count, 1)
        id, data = buffer.new()
        self.assert_id_map(buffer, id, 1)
        self.assertEqual(buffer.count, 2)
        id, data = buffer.new()

    def test_full(self):
        buffer = TurtleBuffer('shape', 2)
        buffer.new()
        buffer.new()
        with self.assertRaises(TurtleBuffer.Full):
            buffer.new()

    def test_copy(self):
        buffer = TurtleBuffer('shape', 2)
        buffer.new([1] * TURTLE_DATA_SIZE)
        buffer.new([2] * TURTLE_DATA_SIZE)
        new = TurtleBuffer.copy(buffer, 4)
        self.assertEqual(len(new.data), 4 * TURTLE_DATA_SIZE)
        self.assert_turtle_data(new, 0, [1] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(new, 1, [2] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(new, 2, [0] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(new, 3, [0] * TURTLE_DATA_SIZE)

    def test_copy_must_be_bigger(self):
        buffer = TurtleBuffer('shape', 4)
        with self.assertRaises(AssertionError):
            TurtleBuffer.copy(buffer, 4)

    def test_remove_end(self):
        buffer = TurtleBuffer('shape', 4)
        id0, data = buffer.new([1] * TURTLE_DATA_SIZE)
        id1, data = buffer.new([2] * TURTLE_DATA_SIZE)
        id2, data = buffer.new([3] * TURTLE_DATA_SIZE)
        self.assert_id_map(buffer, id2, 2)
        buffer.remove(id2)
        self.assertEqual(buffer.count, 2)
        self.assert_id_map(buffer, id0, 0)
        self.assert_id_map(buffer, id1, 1)
        self.assertNotIn(id2, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)
        self.assert_turtle_data(buffer, 0, [1] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 1, [2] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 2, [0] * TURTLE_DATA_SIZE)

    def test_remove_start(self):
        buffer = TurtleBuffer('shape', 4)
        id0, data = buffer.new([1] * TURTLE_DATA_SIZE)
        id1, data = buffer.new([2] * TURTLE_DATA_SIZE)
        id2, data = buffer.new([3] * TURTLE_DATA_SIZE)
        self.assert_id_map(buffer, id0, 0)
        buffer.remove(id0)
        self.assertEqual(buffer.count, 2)
        self.assert_id_map(buffer, id1, 1)
        self.assert_id_map(buffer, id2, 0)
        self.assertNotIn(id0, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)
        self.assert_turtle_data(buffer, 0, [3] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 1, [2] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 2, [0] * TURTLE_DATA_SIZE)

    def test_remove_middle(self):
        buffer = TurtleBuffer('shape', 4)
        id0, data = buffer.new([1] * TURTLE_DATA_SIZE)
        id1, data = buffer.new([2] * TURTLE_DATA_SIZE)
        id2, data = buffer.new([3] * TURTLE_DATA_SIZE)
        self.assert_id_map(buffer, id1, 1)
        buffer.remove(id1)
        self.assertEqual(buffer.count, 2)
        self.assert_id_map(buffer, id0, 0)
        self.assert_id_map(buffer, id2, 1)
        self.assertNotIn(id1, buffer.id_to_index)
        self.assertNotIn(2, buffer.index_to_id)
        self.assert_turtle_data(buffer, 0, [1] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 1, [3] * TURTLE_DATA_SIZE)
        self.assert_turtle_data(buffer, 2, [0] * TURTLE_DATA_SIZE)

    def test_remove_then_add(self):
        buffer = TurtleBuffer('shape', 4)
        id0, data = buffer.new([1] * TURTLE_DATA_SIZE)
        id1, data = buffer.new([2] * TURTLE_DATA_SIZE)
        id2, data = buffer.new([3] * TURTLE_DATA_SIZE)
        buffer.remove(id2)
        self.assertEqual(buffer.count, 2)
        # check data was zeroed
        self.assert_turtle_data(buffer, 2, [0] * TURTLE_DATA_SIZE)

        id3, data = buffer.new([4] * TURTLE_DATA_SIZE)
        self.assertEqual(buffer.count, 3)
        # check reuses previously removed turtle's space
        self.assert_turtle_data(buffer, 2, [4] * TURTLE_DATA_SIZE)

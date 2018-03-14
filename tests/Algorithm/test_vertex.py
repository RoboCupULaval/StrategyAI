# Under MIT licence, see LICENCE.txt

import unittest

from ai.Algorithm.Graph.Vertex import Vertex

__author__ = 'RoboCupULaval'


def return_true():
    return True


def return_false():
    return 1 == 2


class TestVertex(unittest.TestCase):
    def setUp(self):
        self.vertex1 = Vertex(1, return_true)
        self.vertex2 = Vertex(123, return_false)

    def test_init(self):
        self.assertEqual(self.vertex1.next_node, 1)
        self.assertEqual(self.vertex1.condition, return_true)
        self.assertRaises(AssertionError, Vertex, 1.2, return_true)
        self.assertRaises(AssertionError, Vertex, -4, return_true)
        self.assertRaises(AssertionError, Vertex, 2, "not a function")

    def test_evaluate_condition(self):
        self.assertTrue(self.vertex1.evaluate_condition())
        self.assertFalse(self.vertex2.evaluate_condition())

    def test_str(self):
        expected_string = "Next node: " + str(self.vertex1.next_node) + " Condition: " + self.vertex1.condition.__name__
        self.assertEqual(str(self.vertex1), expected_string)

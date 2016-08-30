# Under MIT licence, see LICENCE.txt

import unittest
from ai.Algorithm.Graph import *
from ai.InfoManager import InfoManager
from ai.STA.Tactic.Stop import Stop

__author__ = 'RoboCupULaval'


def foo():
    return True


def foo2():
    return 1 == 2


class TestVertex(unittest.TestCase):
    def setUp(self):
        self.vertex1 = Vertex(1, foo)
        self.vertex2 = Vertex(123, foo2)

    def test_init(self):
        self.assertEqual(self.vertex1.next_node, 1)
        self.assertEqual(self.vertex1.condition, foo)
        self.assertRaises(AssertionError, Vertex, 1.2, foo)
        self.assertRaises(AssertionError, Vertex, -4, foo)
        self.assertRaises(AssertionError, Vertex, 2, "not a function")

    def test_evaluate_condition(self):
        self.assertTrue(self.vertex1.evaluate_condition())
        self.assertFalse(self.vertex2.evaluate_condition())

    def test_str(self):
        expected_string = "Next node: " + str(self.vertex1.next_node) + " Condition: " + self.vertex1.condition.__name__
        self.assertEqual(str(self.vertex1), expected_string)


class TestNode(unittest.TestCase):
    def setUp(self):
        self.info_manager = InfoManager()
        self.tactic = Stop(self.info_manager, 0)
        self.node1 = Node(self.tactic)

    def test_init(self):
        self.assertRaises(AssertionError, Node, "not a tactic")
        self.assertIsInstance(self.node1.tactic, Tactic)
        self.assertEqual(len(self.node1.vertices), 0)

    def test_add_vertex(self):
        pass

    def test_evaluate(self):
        pass


class TestGraph(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == "__main__":
    unittest.main()

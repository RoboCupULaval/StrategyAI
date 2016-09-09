# Under MIT licence, see LICENCE.txt

import unittest
from ai.Algorithm.Node import Node
from ai.Algorithm.Vertex import Vertex
from ai.InfoManager import InfoManager
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.Stop import Stop

__author__ = 'RoboCupULaval'


def foo():
    return True


class TestNode(unittest.TestCase):
    def setUp(self):
        self.info_manager = InfoManager()
        self.tactic1 = GoalKeeper(self.info_manager, 0)
        self.tactic2 = Stop(self.info_manager, 0)
        self.node1 = Node(self.tactic1)
        self.node2 = Node(self.tactic2)
        self.vertex1 = Vertex(0, foo)

    def test_init(self):
        self.assertRaises(AssertionError, Node, "not a tactic")
        self.assertIsInstance(self.node1.tactic, Tactic)
        self.assertEqual(len(self.node1.vertices), 0)

    def test_add_vertex(self):
        self.node1.add_vertex(self.vertex1)
        self.assertEqual(len(self.node1.vertices), 1)

        self.node1.add_vertex(self.vertex1)
        self.assertEqual(len(self.node1.vertices), 1)  # il ne peut y avoir qu'un vertex entre deux noeuds dans un sens

    def test_remove_vertex(self):
        self.node1.add_vertex(self.vertex1)
        self.node1.remove_vertex(420)
        self.assertEqual(len(self.node1.vertices), 1)
        self.node1.remove_vertex(0)
        self.assertEqual(len(self.node1.vertices), 0)

    def test_exec(self):
        pass

    def test_str(self):
        pass

if __name__ == "__main__":
    unittest.main()

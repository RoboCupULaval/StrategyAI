# Under MIT licence, see LICENCE.txt

import unittest
from unittest.mock import create_autospec


from ai.Algorithm.Graph.Node import Node
from ai.Algorithm.Graph.Vertex import Vertex

from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags


class TestNode(unittest.TestCase):

    def setUp(self):
        self.aTactic = TestNode._create_mock_tactic("A command")
        self.anotherTactic = TestNode._create_mock_tactic("Another command")
        self.node1 = Node(self.aTactic)
        self.node2 = Node(self.anotherTactic)
        self.vertex1 = Vertex(self.node1, lambda: True)
        self.vertex2 = Vertex(self.node2, lambda: False)

    @staticmethod
    def _create_mock_tactic(command):
        tactic = create_autospec(Tactic)
        tactic.exec = lambda: command
        return tactic

    def test_init(self):
        with self.assertRaises(AssertionError):
            Node("not a tactic")
        self.assertIsInstance(self.node2.tactic, Tactic)
        assert len(self.node2.vertices) == 0

    def test_add_vertex(self):
        with self.assertRaises(AssertionError):
            self.node1.add_vertex("not a vertex")
        self.node1.add_vertex(self.vertex1)
        assert len(self.node1.vertices) == 1

        self.node1.add_vertex(self.vertex1)
        assert len(self.node1.vertices) == 1  # il ne peut y avoir qu'un vertex entre deux noeuds dans un sens

        self.node1.add_vertex(self.vertex2)
        assert len(self.node1.vertices) == 2

    def test_exec(self):
        self.node1.add_vertex(self.vertex1)
        self.node1.add_vertex(self.vertex2)
        command_from_tactic, next_node = self.node1.exec()
        assert next_node == self.node1
        assert command_from_tactic == self.aTactic.exec()

        self.node2.add_vertex(self.vertex2)
        command_from_tactic, next_node = self.node2.exec()
        assert next_node is self.node2
        assert command_from_tactic == self.anotherTactic.exec()

    def test_set_flag(self):
        with self.assertRaises(AssertionError):
            self.node1.set_flag("not a flag")
        self.node1.set_flag(Flags.SUCCESS)
        assert self.node1.tactic.status_flag == Flags.SUCCESS

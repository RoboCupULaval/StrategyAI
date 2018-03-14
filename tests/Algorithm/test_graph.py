# Under MIT licence, see LICENCE.txt

import unittest
from unittest.mock import create_autospec, MagicMock

from ai.STA.Tactic.tactic import Tactic
from ai.Algorithm.Graph.Graph import Graph
from ai.Algorithm.Graph.Node import Node

__author__ = "Maxime Gagnon-Legault, and others"


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_get_node_tactic(self):
        a_node = self._create_mock_node()
        self.graph.add_node(a_node)

        assert self.graph.get_current_tactic() == a_node.tactic

    def test_exec_graph_node(self):
        a_node = self._create_mock_node()
        self.graph.add_node(a_node)

        self.graph.exec()

        a_node.exec.assert_any_call()

    def test_exec_two_linked_nodes(self):
        a_node = TestGraph._create_mock_node(id_next_node=1)
        another_node = TestGraph._create_mock_node()
        self.graph.add_node(a_node)
        self.graph.add_node(another_node)

        self.graph.exec()
        self.graph.exec()

        a_node.exec.assert_any_call()
        another_node.exec.assert_any_call()

    def test_exec_first_node_only(self):
        a_node = TestGraph._create_mock_node()
        another_node = TestGraph._create_mock_node()
        self.graph.add_node(a_node)
        self.graph.add_node(another_node)

        self.graph.exec()
        self.graph.exec()

        a_node.exec.assert_any_call()
        another_node.exec.assert_not_called()

    @staticmethod
    def _create_mock_node(id_next_node=-1):
        node = create_autospec(Node)
        node.tactic = TestGraph._create_mock_tactic("my command")
        node.exec = MagicMock(return_value=("my command", id_next_node))
        return node

    @staticmethod
    def _create_mock_tactic(command):
        tactic = create_autospec(Tactic)
        tactic.exec = lambda: command
        return tactic

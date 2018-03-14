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

    def test_givenAGraphWithANode_whenGetCurrentTactic_thenReturnTacticOfANode(self):
        a_node = self._create_mock_node()
        self.graph.add_node(a_node)

        assert self.graph.get_current_tactic() == a_node.tactic

    def test_givenAGraphWithANode_whenExecGraph_thenNodeIsCall(self):
        a_node = self._create_mock_node()
        self.graph.add_node(a_node)

        self.graph.exec()

        a_node.exec.assert_any_call()

    def test_givenAGraphWithTwoNodeLinked_whenExecTwice_thenBothNodeAreCalled(self):
        another_node = TestGraph._create_mock_node()
        a_node = TestGraph._create_mock_node(another_node)
        self.graph.add_node(a_node)
        self.graph.add_node(another_node)

        self.graph.exec()
        self.graph.exec()

        a_node.exec.assert_any_call()
        another_node.exec.assert_any_call()

    def test_givenAGraphWithTwoNodeUnLinked_whenExecTwice_thenOnlyTheFirstNodeIsCalled(self):
        a_node = TestGraph._create_mock_node()
        another_node = TestGraph._create_mock_node()
        self.graph.add_node(a_node)
        self.graph.add_node(another_node)

        self.graph.exec()
        self.graph.exec()

        a_node.exec.assert_any_call()
        another_node.exec.assert_not_called()

    @staticmethod
    def _create_mock_node(next_node=None):
        node = create_autospec(Node)
        node.tactic = TestGraph._create_mock_tactic("my command")
        node.exec = MagicMock(return_value=("my command", next_node))
        return node

    @staticmethod
    def _create_mock_tactic(command):
        tactic = create_autospec(Tactic)
        tactic.exec = lambda: command
        return tactic

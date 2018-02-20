# Under MIT licence, see LICENCE.txt
from unittest.mock import create_autospec, MagicMock

from ai.STA.Tactic.tactic import Tactic

__author__ = "Maxime Gagnon-Legault, and others"

import unittest

from ai.Algorithm.Graph.Graph import Graph
from ai.Algorithm.Graph.Node import Node



class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_givenAGraphWithANode_whenGetCurrentTactic_thenReturnTacticOfANode(self):
        aNode = self._create_mock_node()
        self.graph.add_node(aNode)

        assert self.graph.get_current_tactic() == aNode.tactic

    def test_givenAGraphWithANode_whenExecGraph_thenNodeIsCall(self):
        aNode = self._create_mock_node()
        self.graph.add_node(aNode)

        self.graph.exec()

        aNode.exec.assert_any_call()

    def test_givenAGraphWithTwoNodeLinked_whenExecTwice_thenBothNodeAreCalled(self):
        aNode = self._create_mock_node(id_next_node=1)
        anotherNode = self._create_mock_node()
        self.graph.add_node(aNode)
        self.graph.add_node(anotherNode)

        self.graph.exec()
        self.graph.exec()

        aNode.exec.assert_any_call()
        anotherNode.exec.assert_any_call()

    def test_givenAGraphWithTwoNodeUnLinked_whenExecTwice_thenOnlyTheFirstNodeIsCalled(self):
        aNode = self._create_mock_node()
        anotherNode = self._create_mock_node()
        self.graph.add_node(aNode)
        self.graph.add_node(anotherNode)

        self.graph.exec()
        self.graph.exec()

        aNode.exec.assert_any_call()
        anotherNode.exec.assert_not_called()

    def _create_mock_node(self, id_next_node=-1):
        node = create_autospec(Node)
        node.tactic = self._create_mock_tactic("my command")
        node.exec = MagicMock(return_value=("my command", id_next_node))
        return node

    def _create_mock_tactic(self, command):
        tactic = create_autospec(Tactic)
        tactic.exec = lambda : command
        return tactic

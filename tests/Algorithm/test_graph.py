# Under MIT licence, see LICENCE.txt

import unittest
from ai.Algorithm.Graph import Graph, EmptyGraphException
from ai.Algorithm.Node import Node
from ai.Algorithm.Vertex import Vertex
from ai.states.game_state import GameState
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.tactic_constants import Flags
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

from ai.Util.ai_command import AICommand, AICommandType

__author__ = 'RoboCupULaval'


def foo():
    return True


def foo2():
    return False


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.empty_graph = Graph()
        self.graph1 = Graph()
        self.tactic1 = Stop(self.game_state, 1)
        self.tactic2 = GoToPosition(self.game_state, 0, Pose(Position(500, 0), 0))
        self.node1 = Node(self.tactic1)
        self.node2 = Node(self.tactic2)
        self.vertex1 = Vertex(1, foo)
        self.graph1.add_node(self.node1)
        self.graph1.add_node(self.node2)
        self.graph1.add_vertex(0, 1, foo)

    def test_init(self):
        self.assertEqual(self.empty_graph.current_node, 0)
        self.assertEqual(len(self.empty_graph.nodes), 0)

    def test_get_current_tactic_name(self):
        self.assertEqual(self.graph1.get_current_tactic_name(), "Stop")
        self.assertEqual(self.empty_graph.get_current_tactic_name(), None)
        self.empty_graph.add_node(self.node2)
        self.assertEqual(self.empty_graph.get_current_tactic_name(), "GoToPosition")

    def test_get_current_tactic(self):
        self.assertIsInstance(self.graph1.get_current_tactic(), Stop)
        self.assertEqual(self.empty_graph.get_current_tactic(), None)
        self.empty_graph.add_node(self.node2)
        self.assertIsInstance(self.empty_graph.get_current_tactic(), GoToPosition)

    def test_add_node(self):
        self.assertEqual(len(self.graph1.nodes), 2)
        self.assertRaises(AssertionError, self.graph1.add_node, "not a node")

    def test_remove_node(self):
        self.assertRaises(AssertionError, self.graph1.remove_node, "not an int")
        self.assertRaises(AssertionError, self.graph1.remove_node, -1)
        self.assertRaises(AssertionError, self.graph1.remove_node, 420)
        self.graph1.remove_node(1)
        self.assertEqual(len(self.graph1.nodes), 1)
        self.assertEqual(len(self.graph1.nodes[0].vertices), 0)

    def test_add_vertex(self):
        self.assertEqual(len(self.graph1.nodes[0].vertices), 1)
        self.assertRaises(AssertionError, self.graph1.add_vertex, "not an int", 1, foo)
        self.assertRaises(AssertionError, self.graph1.add_vertex, -1, 1, foo)
        self.assertRaises(AssertionError, self.graph1.add_vertex, 420, 1, foo)
        self.assertRaises(AssertionError, self.graph1.add_vertex, 0, "not an int", foo)
        self.assertRaises(AssertionError, self.graph1.add_vertex, 0, -1, foo)
        self.assertRaises(AssertionError, self.graph1.add_vertex, 0, 420, foo)
        self.assertRaises(AssertionError, self.graph1.add_vertex, 0, 1, "not a callable")
        self.graph1.add_vertex(0, 1, foo)
        self.assertEqual(len(self.graph1.nodes[0].vertices), 1)

    def test_remove_vertex(self):
        self.assertRaises(AssertionError, self.graph1.remove_vertex, "not an int", 1)
        self.assertRaises(AssertionError, self.graph1.remove_vertex, -1, 1)
        self.assertRaises(AssertionError, self.graph1.remove_vertex, 420, 1)
        self.assertRaises(AssertionError, self.graph1.remove_vertex, 0, "not an int")
        self.assertRaises(AssertionError, self.graph1.remove_vertex, 0, -1)
        self.assertRaises(AssertionError, self.graph1.remove_vertex, 0, 420)
        self.graph1.add_node(self.node2)
        self.graph1.remove_vertex(0, 2)
        self.assertEqual(len(self.graph1.nodes[0].vertices), 1)
        self.graph1.remove_vertex(0, 1)
        self.assertEqual(len(self.graph1.nodes[0].vertices), 0)

    def test_exec(self):
        next_ai_command = self.graph1.exec()
        expected_ai_command = AICommand(1, AICommandType.STOP)
        self.assertEqual(self.graph1.current_node, 1)
        self.assertEqual(next_ai_command, expected_ai_command)

        self.assertRaises(EmptyGraphException, self.empty_graph.exec)

        self.empty_graph.add_node(self.node2)
        self.empty_graph.add_node(self.node1)
        self.empty_graph.add_vertex(0, 1, foo2)

        next_ai_command = self.empty_graph.exec()
        expected_ai_command = AICommand(0, AICommandType.MOVE,
                                        **{"pose_goal": Pose(Position(500, 0))})
        self.assertEqual(self.empty_graph.current_node, 0)
        self.assertEqual(next_ai_command, expected_ai_command)

        next_ai_command = self.empty_graph.exec()
        expected_ai_command = AICommand(Pose(Position(500, 0), 0), 0)
        self.assertEqual(self.empty_graph.current_node, 0)
        self.assertEqual(next_ai_command, expected_ai_command)

    def test_set_current_node(self):
        self.assertRaises(AssertionError, self.graph1.set_current_node, "not an int")
        self.assertRaises(AssertionError, self.graph1.set_current_node, -1)
        self.assertRaises(AssertionError, self.graph1.set_current_node, 420)
        self.graph1.nodes[0].set_flag(Flags.WIP)
        self.graph1.set_current_node(1)
        self.assertEqual(self.graph1.current_node, 1)
        self.assertEqual(self.graph1.nodes[0].tactic.status_flag, Flags.INIT)

    def test_str(self):
        expected_string = ""
        for i in range(len(self.graph1.nodes)):
            expected_string += "Node " + str(i) + ": " + str(self.graph1.nodes[i]) + "\n"
        self.assertEqual(str(self.graph1), expected_string)

if __name__ == "__main__":
    unittest.main()

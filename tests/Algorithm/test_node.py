# Under MIT licence, see LICENCE.txt

import unittest
from ai.Algorithm.Node import Node
from ai.Algorithm.Vertex import Vertex
from ai.states.game_state import GameState
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.Stop import Stop
from ai.Util.types import AICommand

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


def foo():
    return True


def foo2():
    return False


class TestNode(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.game_state._update_player(0, Pose(Position(-4450, 0), 0))
        self.tactic1 = GoalKeeper(self.game_state, 0)
        self.tactic2 = Stop(self.game_state, 1)
        self.node1 = Node(self.tactic1)
        self.node2 = Node(self.tactic2)
        self.vertex1 = Vertex(0, foo)
        self.vertex2 = Vertex(1, foo2)

    def test_init(self):
        self.assertRaises(AssertionError, Node, "not a tactic")
        self.assertIsInstance(self.node2.tactic, Tactic)
        self.assertEqual(len(self.node2.vertices), 0)

    def test_add_vertex(self):
        self.assertRaises(AssertionError, self.node1.add_vertex, "not a vertex")
        self.node1.add_vertex(self.vertex1)
        self.assertEqual(len(self.node1.vertices), 1)

        self.node1.add_vertex(self.vertex1)
        self.assertEqual(len(self.node1.vertices), 1)  # il ne peut y avoir qu'un vertex entre deux noeuds dans un sens

        self.node1.add_vertex(self.vertex2)
        self.assertEqual(len(self.node1.vertices), 2)

    def test_remove_vertex(self):
        self.assertRaises(AssertionError, self.node1.remove_vertex, "not an int")
        self.assertRaises(AssertionError, self.node1.remove_vertex, -1)
        self.node1.add_vertex(self.vertex1)
        self.node1.remove_vertex(420)
        self.assertEqual(len(self.node1.vertices), 1)
        self.node1.remove_vertex(0)
        self.assertEqual(len(self.node1.vertices), 0)

    def test_exec(self):
        self.node1.add_vertex(self.vertex1)
        self.node1.add_vertex(self.vertex2)
        next_ai_command, next_node = self.node1.exec()
        self.assertEqual(next_node, 0)
        expected_aicmd = AICommand(Pose(Position(-4000, 0), 0), 0)
        self.assertEqual(next_ai_command, expected_aicmd)

        self.node2.add_vertex(self.vertex2)
        expected_aicmd = AICommand(None, 0)
        next_ai_command, next_node = self.node2.exec()
        self.assertEqual(next_ai_command, expected_aicmd)
        self.assertEqual(next_node, -1)

    def test_str(self):
        self.node1.add_vertex(self.vertex1)
        self.node1.add_vertex(self.vertex2)
        expected_string = "Tactic: GoalKeeper    Vertices: "
        for vertex in self.node1.vertices:
            expected_string += "\n    " + str(vertex)
        self.assertEqual(str(self.node1), expected_string)

if __name__ == "__main__":
    unittest.main()

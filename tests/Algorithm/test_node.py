# Under MIT licence, see LICENCE.txt

import unittest

from RULEngine.GameDomainObjects.OurPlayer import OurPlayer
from RULEngine.GameDomainObjects.Ball import Ball
from RULEngine.GameDomainObjects.Game import Game
from RULEngine.GameDomainObjects.Referee import Referee
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from RULEngine.Util.team_color_service import TeamColorService, TeamColor
from ai.Algorithm.Graph.Node import Node
from ai.Algorithm.Graph.Vertex import Vertex
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.game_state import GameState
from config.config_service import ConfigService

__author__ = 'RoboCupULaval'


def foo():
    return True


def foo2():
    return False


A_GOAL_PLAYER_ID = 0
A_PLAYER_ID = 1
class TestNode(unittest.TestCase):
    def setUp(self):
        config_service = ConfigService().load_file("config/sim_standard.cfg")
        self.game_state = GameState()
        self.game = Game()
        self.game.set_referee(Referee())
        self.game.ball = Ball()
        game_world = ReferenceTransferObject(self.game)
        game_world.set_team_color_svc(TeamColorService(TeamColor.YELLOW))
        self.game_state.set_reference(game_world)
        self.game_state.game.friends.players[0].pose = Pose(Position(-4450, 0), 0)
        self.tactic1 = GoalKeeper(self.game_state, self.game_state.game.friends.players[A_GOAL_PLAYER_ID])
        self.tactic2 = Stop(self.game_state, self.game_state.game.friends.players[A_PLAYER_ID])
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

    @unittest.skip("thinkin we should have generic tactic for test purpose, this is infuriating")
    def test_exec(self):
        self.node1.add_vertex(self.vertex1)
        self.node1.add_vertex(self.vertex2)
        next_ai_command, next_node = self.node1.exec()
        self.assertEqual(next_node, 0)
        expected_aicmd = AICommand(0, AICommandType.MOVE, **{"pose_goal": Pose(Position(-4000, 0), 0)})
        self.assertEqual(next_ai_command, expected_aicmd)

        self.node2.add_vertex(self.vertex2)
        expected_aicmd = AICommand(0, AICommandType.STOP)#, **{"pose_goal": Pose(Position(-4000, 0), 0)})
        next_ai_command, next_node = self.node2.exec()
        self.assertEqual(next_ai_command, expected_aicmd)
        self.assertEqual(next_node, -1)


    def test_set_flag(self):
        self.assertRaises(AssertionError, self.node1.set_flag, "not a flag")
        self.node1.set_flag(Flags.SUCCESS)
        self.assertEqual(self.node1.tactic.status_flag, Flags.SUCCESS)

if __name__ == "__main__":
    unittest.main()

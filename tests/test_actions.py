# Under MIT license, see LICENSE.txt

import unittest
from math import pi, atan, sqrt

from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import *
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.MoveToDribblingBall import MoveToDribblingBall
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.states.game_state import GameState


class TestActions(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        self.game_state = GameState()
        self.player_id = 1  # random integer


    def test_move_to(self):
        self.pose = Pose(Position(0, 0, 0), orientation=0.0)
        self.move = MoveToPosition(self.game_state, self.player_id, self.pose)
        self.assertEqual(str(MoveToPosition.exec(self.move)),
                         "AICommand(move_destination=[(x=0.0, y=0.0, z=0.0), theta=0.0], kick_strength=0)")

        self.pose = Pose(Position(0.5, 0.3, 0.2), orientation=3.2)
        self.move = MoveToPosition(self.game_state, self.player_id, self.pose)
        self.assertEqual(str(MoveToPosition.exec(self.move)), "AICommand(move_destination=[(x=0.5, y=0.3, z=0.2), theta=" +
                         "-3.083185307179586], kick_strength=0)")

    def test_idle(self):
        self.idle = Idle(self.game_state, self.player_id)
        current_pose = None
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0)"
        self.assertEqual(str(Idle.exec(self.idle)), current_pose_string)

    def test_GrabBall(self):
        self.grab_ball = GetBall(self.game_state, self.player_id)
        self.game_state._update_ball_position(Position(5, 0))
        ai_cmd = self.grab_ball.exec()
        ai_cmd_expected = AICommand(Pose(Position(5, 0)), 0)
        print(self.game_state.get_player_pose(self.player_id))
        print(ai_cmd)
        print(ai_cmd_expected)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        self.game_state._update_ball_position(Position(-5, 5))
        ai_cmd = self.grab_ball.exec()
        ai_cmd_expected = AICommand(Pose(Position(-5, 5), 3*pi/4), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)


    def test_MoveWithBall(self):
        self.move_with_ball = MoveToDribblingBall(self.game_state, self.player_id, Position(100, 0))
        self.game_state._update_ball_position(Position(5, 0))
        ai_cmd = self.move_with_ball.exec()
        ai_cmd_expected = AICommand(Pose(Position(100, 0), 0), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        self.game_state._update_ball_position(Position(5, 2))
        ai_cmd = self.move_with_ball.exec()
        ai_cmd_expected = AICommand(Pose(Position(100, 0), atan(2/5)), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

    def test_GoBetween(self):
        # test avec une droite verticale
        self.go_between = GoBetween(self.game_state, self.player_id, Position(100, 100), Position(100, -100),
                                    Position(200, 0))
        ai_cmd = self.go_between.exec()
        ai_cmd_expected = AICommand(Pose(Position(100, 0), 0), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test avec une droite horizontale
        self.go_between = GoBetween(self.game_state, self.player_id, Position(100, 100), Position(-100, 100),
                                    Position(0, 200))
        ai_cmd = self.go_between.exec()
        ai_cmd_expected = AICommand(Pose(Position(0, 100), pi/2), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test avec une droite quelconque
        self.go_between = GoBetween(self.game_state, self.player_id, Position(0, 500), Position(500, 0),
                                    Position(-300, -300))
        ai_cmd = self.go_between.exec()
        ai_cmd_expected = AICommand(Pose(Position(250, 250), -3*pi/4), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test destination calculée derrière position1
        self.go_between = GoBetween(self.game_state, self.player_id, Position(1000, 75), Position(1500, -250),
                                    Position(0, 0), 180)
        ai_cmd = self.go_between.exec()
        ai_cmd_expected = AICommand(Pose(Position(1150, -23), 3.1215), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test destination calculée derrière position2
        self.go_between = GoBetween(self.game_state, self.player_id, Position(-100, 50), Position(-50, 50),
                                    Position(-60.0 + sqrt(3), 51.0), 10)
        ai_cmd = self.go_between.exec()
        ai_cmd_expected = AICommand(Pose(Position(-60, 50), 0.5235), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test correction pour respecter la distance minimale
        self.go_between = GoBetween(self.game_state, self.player_id, Position(-500, 25), Position(1, 25),
                                    Position(-179, 0), 180)
        ai_cmd = self.go_between.exec()
        ai_cmd_expected = AICommand(Pose(Position(-179, 25), -pi/2), 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test distance entre les positions insuffisantes
        self.assertRaises(AssertionError, GoBetween, self.game_state, self.player_id, Position(1, 1),
                          Position(-1, -1), 50)

    def test_GoBehind(self):
        # TODO: faire davantage de cas de test
        distance_behind = 500

        # test avec une droite quelconque
        self.go_behind = GoBehind(self.game_state, self.player_id, Position(1.5, 2.3), Position(18.3, 27.8),
                                  distance_behind)
        aicmd_obtenu = GoBehind.exec(self.go_behind)
        aicmd_cible = AICommand(Pose(Position(-273, -415), 0.9882), 0)
        self.assertEqual(aicmd_obtenu, aicmd_cible)

        # test avec une droite verticale
        self.go_behind = GoBehind(self.game_state, self.player_id, Position(1000, 250.3), Position(1000, 725.8),
                                  distance_behind)
        aicmd_obtenu = GoBehind.exec(self.go_behind)
        aicmd_cible = AICommand(Pose(Position(1000, -249), 1.5707), 0)
        self.assertEqual(aicmd_obtenu, aicmd_cible)

        # test avec une droite horizontale
        self.go_behind = GoBehind(self.game_state, self.player_id, Position(175.8, -200.34), Position(-276.8, -200.34),
                                  distance_behind)
        aicmd_obtenu = GoBehind.exec(self.go_behind)
        aicmd_cible = AICommand(Pose(Position(675, -200), -3.1415), 0)
        self.assertEqual(aicmd_obtenu, aicmd_cible)

    def test_kick(self):

        # test avec la valeur 0 (nulle)
        self.kick = Kick(self.game_state, self.player_id, 0)
        current_pose = self.game_state.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0)"
        self.assertEqual(str(Kick.exec(self.kick)), current_pose_string)

        # test avec la valeur 1 (force maximale)
        self.kick = Kick(self.game_state, self.player_id, 1)
        current_pose = self.game_state.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=1)"
        self.assertEqual(str(Kick.exec(self.kick)), current_pose_string)

        # test avec la valeur 0.3 (force intermediaire)
        self.kick = Kick(self.game_state, self.player_id, 0.3)
        current_pose = self.game_state.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0.3)"
        self.assertEqual(str(Kick.exec(self.kick)), current_pose_string)

    def test_ProtectGoal(self):
        # test de base
        self.game_state._update_player(0, Pose(Position(4450, 10), 0))
        self.game_state._update_ball_position(Position(0, 0))
        self.protectGoal = ProtectGoal(self.game_state, 0)

        aicmd_obtenu = self.protectGoal.exec()
        aicmd_cible = AICommand(Pose(Position(4000, 0), -pi), 0)
        self.assertEqual(aicmd_obtenu, aicmd_cible)

        # test distance max < distance min
        self.assertRaises(AssertionError, ProtectGoal, self.game_state, 0, True, 50, 40)

if __name__ == "__main__":
    unittest.main()

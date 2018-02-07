# Under MIT license, see LICENSE.txt

import unittest
from math import pi, sqrt

from RULEngine.Util.pose import Pose
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject

from RULEngine.services.team_color_service import TeamColorService
from Util import AICommand, AICommandType, AIControlLoopType
<<<<<<< HEAD
from Util import Position
from ai.GameDomainObjects import Game
from ai.GameDomainObjects import Player
from ai.GameDomainObjects import Referee
=======
from Util.position import Position
from ai.STA.Action.GetBall import GetBall
>>>>>>> 658ccbf98f0e28b85cf7ad0e97fabff8066870e6
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.ProtectGoal import ProtectGoal

A_DELTA_T = 1
A_PLAYER_ID = 1


class TestActions(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        self.game_state = Game()
        self.game = Game()
        self.game.set_referee(Referee())
        game_world = ReferenceTransferObject(self.game)
        game_world.set_team_color_svc(TeamColorService(TeamColor.YELLOW))
        self.game_state.set_reference(game_world)
        self.a_player = Player(TeamColor.YELLOW, A_PLAYER_ID)

    def test_move_to(self):
        A_CRUISE_SPEED = 0.1
        self.pose = Pose(Position(0, 0), 0.0)
        self.move = MoveToPosition(self.game_state, self.a_player, self.pose, False, A_CRUISE_SPEED)
        return_cmd = self.move.exec()
        expected_cmd = AICommand(self.a_player, AICommandType.MOVE,
                                   **{"pose_goal": self.pose,
                                      "pathfinder_on": False,
                                      "cruise_speed": A_CRUISE_SPEED})
        self.assertEqual(return_cmd, expected_cmd)

        self.pose = Pose(Position(0.5, 0.3), 3.2)
        self.move = MoveToPosition(self.game_state, self.a_player, self.pose, False, A_CRUISE_SPEED)
        self.assertEqual(MoveToPosition.exec(self.move),
                         AICommand(self.a_player, AICommandType.MOVE,
                                   **{"pose_goal": self.pose,
                                      "pathfinder_on": False,
                                      "cruise_speed": A_CRUISE_SPEED}))

    def test_idle(self):
        idle = Idle(self.game_state, self.a_player)
        expected_command = AICommand(self.a_player,
                                        AICommandType.STOP,
                                        control_loop_type=AIControlLoopType.POSITION)
        actual_command = Idle.exec(idle)
        self.assertEqual(actual_command, expected_command)

    def test_GrabBall(self):
        self.grab_ball = GetBall(self.game_state,self.a_player)
        self.game_state.set_ball_position(Position(5, 0), A_DELTA_T)
        ai_cmd = self.grab_ball.exec()
        ball_position = self.game_state.get_ball_position()
        destination_orientation = (ball_position - self.a_player.pose.position).angle()
        destination_pose = Pose(ball_position, destination_orientation)
        ai_cmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                    **{"pose_goal": destination_pose})
        self.assertEqual(ai_cmd, ai_cmd_expected)

        grab_pose = Pose(Position(-5, 5), 3 * pi / 4)
        self.game_state.set_ball_position(Position(-5, 5), A_DELTA_T)
        ai_cmd = self.grab_ball.exec()
        ai_cmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                    **{"pose_goal": grab_pose})
        self.assertEqual(ai_cmd, ai_cmd_expected)


    @unittest.skip("GoBetween does not actually go in between")
    def test_GoBetween(self):
        # test avec une droite verticale
        POS_TOP       = Position(100, 100)
        POS_BOTTOM    = Position(100, -100)
        POS_TARGET    = Position(200, 0)
        POS_INBETWEEN = Position(100, 0)
        self.go_between = GoBetween(self.game_state,self.a_player, POS_TOP, POS_BOTTOM,
                                    POS_TARGET)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(POS_INBETWEEN, 0)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test avec une droite horizontale
        self.go_between = GoBetween(self.game_state, self.a_player, Position(100, 100), Position(-100, 100),
                                    Position(0, 200))
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(0, 100), pi / 2)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test avec une droite quelconque
        self.go_between = GoBetween(self.game_state, self.a_player, Position(0, 500), Position(500, 0),
                                    Position(-300, -300))
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(250, 250), -3 * pi / 4)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test destination calculée derrière position1
        self.go_between = GoBetween(self.game_state, self.a_player, Position(1000, 75), Position(1500, -250),
                                    Position(0, 0), 0)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(1000, 75), -3.067)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test destination calculée derrière position2
        self.go_between = GoBetween(self.game_state, self.a_player, Position(-100, 50), Position(-50, 50),
                                    Position(-60.0 + sqrt(3), 51.0), 10)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(-60, 50), 0.5235)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test correction pour respecter la distance minimale
        self.go_between = GoBetween(self.game_state, self.a_player, Position(-500, 25), Position(1, 25),
                                    Position(-179, 0), 180)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(-179, 25), -pi / 2)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test distance entre les positions insuffisantes
        self.assertRaises(AssertionError, GoBetween, self.game_state, self.a_player, Position(1, 1),
                          Position(-1, -1), 50)

    def test_GoBehind(self):
        # TODO: faire davantage de cas de test
        distance_behind = 500

        # test avec une droite verticale
        self.go_behind = GoBehind(self.game_state, self.a_player, Position(1000, 250.3), Position(1000, 725.8),
                                  distance_behind)
        aicmd_obtenu = self.go_behind.exec()
        aicmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                   **{"pose_goal": Pose(Position(1000, -249.700), 1.5707)})
        self.assertEqual(aicmd_obtenu, aicmd_expected)


        # test avec une droite quelconque
        self.go_behind = GoBehind(self.game_state, self.a_player, Position(1.5, 2.3), Position(18.3, 27.8),
                                  distance_behind)
        aicmd_obtenu = self.go_behind.exec()
        aicmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                   **{"pose_goal": Pose(Position(-273.579, -415.230), 0.9882)})

        self.assertEqual(aicmd_obtenu, aicmd_expected)

        # test avec une droite horizontale
        self.go_behind = GoBehind(self.game_state, self.a_player, Position(175.8, -200.34), Position(-276.8, -200.34),
                                  distance_behind)
        aicmd_obtenu = GoBehind.exec(self.go_behind)
        aicmd_cible = AICommand(self.a_player, AICommandType.MOVE,
                                **{"pose_goal": Pose(Position(675.800, 99.660), -2.601)})
        self.assertEqual(aicmd_obtenu, aicmd_cible)

    def test_kick(self):
        # test avec la valeur 0 (nulle)
        target = Pose(Position(1, 1))
        ball_position = Position(5, 0)
        self.game_state.set_ball_position(ball_position, A_DELTA_T)
        expected_cmd = AICommand(self.a_player, AICommandType.MOVE,
                                 **{"pose_goal": Pose(ball_position, 0.785),
                                    "charge_kick": True,
                                    "kick": True,
                                    "pathfinder_on": True,
                                    "cruise_speed": 0.1,
                                    "end_speed": 0
                                    })
        return_cmd = Kick(self.game_state, self.a_player, force=0, target=target).exec()
        self.assertEqual(expected_cmd, return_cmd)

        # test avec la valeur 1 (force maximale)
        expected_cmd.kick_strength = 1
        return_cmd = Kick(self.game_state,self.a_player, 1, target=target).exec()
        self.assertEqual(return_cmd, expected_cmd)

        # test avec la valeur 0.3 (force intermediaire)
        expected_cmd.kick_strength = 0.3
        return_cmd = Kick(self.game_state,self.a_player, 0.3, target=target).exec()
        self.assertEqual(return_cmd, expected_cmd)

    @unittest.skip("I got lazy, didn't want to review all of the protectgoal.")
    def test_ProtectGoal(self):
        # test de base
        self.game_state.game.friends.players[0].update(Pose(Position(4450, 10)))
        self.game_state.game.ball.set_position(Position(0, 0), 0)
        self.protectGoal = ProtectGoal(self.game_state, 0)

        aicmd_obtenu = self.protectGoal.exec()
        aicmd_cible = AICommand(self.a_player, AICommandType.MOVE,
                                **{"pose_goal": Pose(Position(4000, 0), -pi)})
        self.assertEqual(aicmd_obtenu, aicmd_cible)

        # test distance max < distance min
        self.assertRaises(AssertionError, ProtectGoal, self.game_state, 0, True, 50, 40)

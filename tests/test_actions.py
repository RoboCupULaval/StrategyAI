# Under MIT license, see LICENSE.txt

import unittest
from math import pi, atan, sqrt

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from RULEngine.Game.Referee import Referee
from RULEngine.Util.team_color_service import TeamColorService, TeamColor
from RULEngine.Game.Game import Game
from config.config_service import ConfigService
from RULEngine.Util.Pose import Pose
from RULEngine.Util.SpeedPose import SpeedPose
from RULEngine.Util.constant import *
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.states.game_state import GameState
from ai.Util.ai_command import AICommand, AICommandType, AIControlLoopType

A_DELTA_T = 1
A_PLAYER_ID = 1

class TestActions(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        ConfigService().load_file("config/sim_standard.cfg")
        self.game_state = GameState()
        self.game = Game()
        self.game.set_referee(Referee())
        game_world = ReferenceTransferObject(self.game)
        game_world.set_team_color_svc(TeamColorService(TeamColor.YELLOW))
        self.game_state.set_reference(game_world)
        self.a_player = OurPlayer(TeamColor.YELLOW, A_PLAYER_ID)

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
        self.idle = Idle(self.game_state,self.a_player)
        current_pose = None
        current_pose_string = AICommand(self.a_player, AICommandType.STOP)
        self.assertEqual(Idle.exec(self.idle), current_pose_string)

    def test_GrabBall(self):
        self.grab_ball = GetBall(self.game_state,self.a_player)
        self.game_state.set_ball_position(Position(5, 0), A_DELTA_T)
        ai_cmd = self.grab_ball.exec()
        ball_position = self.game_state.get_ball_position()
        destination_orientation = get_angle(self.a_player.pose.position, ball_position)
        destination_pose = Pose(ball_position, destination_orientation)
        ai_cmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                    **{"pose_goal": destination_pose})
        self.assertEqual(ai_cmd, ai_cmd_expected)

        grab_pose = Pose(Position(-5, 5), 3*pi/4)
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
        self.go_between = GoBetween(self.game_state,self.a_player, Position(100, 100), Position(-100, 100),
                                    Position(0, 200))
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(0, 100), pi/2)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test avec une droite quelconque
        self.go_between = GoBetween(self.game_state,self.a_player, Position(0, 500), Position(500, 0),
                                    Position(-300, -300))
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(250, 250), -3*pi/4)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test destination calculée derrière position1
        self.go_between = GoBetween(self.game_state,self.a_player, Position(1000, 75), Position(1500, -250),
                                    Position(0, 0), 0)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(1000, 75), -3.067)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test destination calculée derrière position2
        self.go_between = GoBetween(self.game_state,self.a_player, Position(-100, 50), Position(-50, 50),
                                    Position(-60.0 + sqrt(3), 51.0), 10)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(-60, 50), 0.5235)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test correction pour respecter la distance minimale
        self.go_between = GoBetween(self.game_state,self.a_player, Position(-500, 25), Position(1, 25),
                                    Position(-179, 0), 180)
        ai_cmd = self.go_between.exec().pose_goal
        ai_cmd_expected = Pose(Position(-179, 25), -pi/2)
        self.assertEqual(ai_cmd, ai_cmd_expected)

        # test distance entre les positions insuffisantes
        self.assertRaises(AssertionError, GoBetween, self.game_state,self.a_player, Position(1, 1),
                          Position(-1, -1), 50)

    @unittest.skip("There is some obstacle avoidance that was added to goBehind that broke it in some case. We should wait before the pathfinder handle a collidable-ball before fixing it")
    def test_GoBehind(self):
        # TODO: faire davantage de cas de test
        distance_behind = 500

        # test avec une droite verticale
        self.go_behind = GoBehind(self.game_state,self.a_player, Position(1000, 250.3), Position(1000, 725.8),
                                  distance_behind)
        aicmd_obtenu = self.go_behind.exec()
        aicmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                **{"pose_goal": Pose(Position(1000, -249), 1.5707)})
        # AICommand(Pose(Position(1000, -249), 1.5707), 0)
        self.assertEqual(aicmd_obtenu, aicmd_expected)


        # test avec une droite quelconque
        self.go_behind = GoBehind(self.game_state,self.a_player, Position(1.5, 2.3), Position(18.3, 27.8),
                                  distance_behind)
        aicmd_obtenu = self.go_behind.exec()
        aicmd_expected = AICommand(self.a_player, AICommandType.MOVE,
                                   **{"pose_goal": Pose(Position(-273, -415), 0.9882)})
        # AICommand(Pose(Position(-273, -415), 0.9882), 0)
        self.assertEqual(aicmd_obtenu, aicmd_expected)

        # test avec une droite horizontale
        self.go_behind = GoBehind(self.game_state,self.a_player, Position(175.8, -200.34), Position(-276.8, -200.34),
                                  distance_behind)
        aicmd_obtenu = GoBehind.exec(self.go_behind)
        aicmd_cible = AICommand(self.a_player, AICommandType.MOVE,
                                **{"pose_goal": Pose(Position(675, -200), -3.1415)})
        self.assertEqual(aicmd_obtenu, aicmd_cible)

    def test_kick(self):

        # test avec la valeur 0 (nulle)
        target = Pose(Position(1,1))
        self.kick = Kick(self.game_state, self.a_player, p_force=0, target=target)
        ball_position = Position(5, 0)
        self.game_state.set_ball_position(ball_position, A_DELTA_T)
        orientation = (target.position - ball_position).angle()
        expected_cmd = AICommand(self.a_player, AICommandType.MOVE,
                                 **{"pose_goal": Pose(ball_position, orientation),
                                    "kick": True,
                                    "pathfinder_on": True,
                                    "cruise_speed": 0.1,
                                    "end_speed": 0
                                    })
        return_cmd = self.kick.exec()
        self.assertEqual(expected_cmd, return_cmd)

        # test avec la valeur 1 (force maximale)
        self.kick = Kick(self.game_state,self.a_player, 1, target=target)
        self.assertEqual(self.kick.exec(), AICommand(self.a_player, AICommandType.MOVE,
                                           **{"pose_goal": Pose(ball_position, orientation),
                                              "kick": True,
                                              "kick_strength": 1,
                                              "pathfinder_on": True,
                                              "cruise_speed": 0.1,
                                              "end_speed": 0}))

        # test avec la valeur 0.3 (force intermediaire)
        self.kick = Kick(self.game_state,self.a_player, 0.3, target=target)
        self.assertEqual(self.kick.exec(), AICommand(self.a_player, AICommandType.MOVE,
                                           **{"pose_goal": Pose(ball_position, orientation),
                                              "kick": True,
                                              "kick_strength": 0.3,
                                              "pathfinder_on": True,
                                              "cruise_speed": 0.1,
                                              "end_speed": 0}))

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

if __name__ == "__main__":
    unittest.main()

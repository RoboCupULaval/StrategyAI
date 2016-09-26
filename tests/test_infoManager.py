# Under MIT License, see LICENSE.txt
import unittest

from RULEngine.Framework import GameState
from RULEngine.Game import Ball, Field, Team
from RULEngine.Util.Position import Position
from ai.managers.InfoManager import InfoManager

__author__ = 'RoboCupULaval'


class TestInfoManager(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        ball = Ball.Ball()
        self.field = Field.Field(ball)

        blue_team = Team.Team(False)
        yellow_team = Team.Team(True)

        self.info_manager = InfoManager()

        game_state = GameState(self.field, None, blue_team, yellow_team, 0, [])
        self.info_manager.update(game_state)

    def test_can_get_current_play(self):
        self.info_manager.game['play'] = "awesomePlay!"
        self.assertEqual(self.info_manager.get_current_play(), "awesomePlay!")

    def test_can_get_current_play_sequence(self):
        self.info_manager.game['sequence'] = [1,2,3,4]
        self.assertEqual(self.info_manager.get_current_play_sequence(), [1,2,3,4])

    def test_can_set_play(self):
        self.info_manager.set_play('pDance')
        self.assertEqual(self.info_manager.game['play'], 'pDance')

    def test_can_init_play_sequence(self):
        self.info_manager.init_play_sequence()
        self.assertEqual(self.info_manager.game['sequence'], 0)

    def test_can_increase_play_sequence(self):
        self.info_manager.init_play_sequence()
        self.info_manager.inc_play_sequence()
        self.assertEqual(self.info_manager.game['sequence'], 1)
        self.info_manager.inc_play_sequence()
        self.assertEqual(self.info_manager.game['sequence'], 2)

    def test_can_get_player_target(self):
        # ToDo : Determine what is a target, tested with dummy value
        self.info_manager.friend['1']['target'] = "Score"
        self.assertEqual(self.info_manager.get_player_target(1), 'Score')

    def test_fails_get_player_target_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_target(42)

    def test_can_get_player_goal(self):
        # ToDo : Determine what is a target, tested with dummy value
        self.info_manager.friend['1']['goal'] = "Score more!"
        self.assertEqual(self.info_manager.get_player_goal(1), 'Score more!')

    def test_fails_get_player_goal_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_goal(42)

    def test_fails_get_player_skill_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_skill(42)

    def test_can_get_player_tactic(self):
        self.info_manager.tactics[1] = "Kick Properly"
        self.assertEqual(self.info_manager.get_player_tactic(1), 'Kick Properly')

    def test_fails_get_player_tactic_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_tactic(42)

    def test_can_get_player_position(self):
        self.info_manager.friend['1']['position'] = (1, 2, 3)
        self.assertEqual(self.info_manager.get_player_position(1), (1, 2, 3))

    def test_fails_get_player_position_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_position(42)

    def test_can_get_player_pose(self):
        self.info_manager.friend['1']['pose'] = ((1, 2, 3), 10.0)
        self.assertEqual(self.info_manager.get_player_pose(1), ((1, 2, 3), 10.0))

    def test_fails_get_player_pose_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_pose(42)

    def test_can_get_player_orientation(self):
        self.info_manager.friend['1']['orientation'] = 10.0
        self.assertEqual(self.info_manager.get_player_orientation(1), 10.0)

    def test_fails_get_player_orientation_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_orientation(42)

    def test_can_get_player_kick_state(self):
        self.info_manager.friend['1']['kick'] = True
        self.assertEqual(self.info_manager.get_player_kick_state(1), True)

    def test_fails_get_player_kick_state_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_kick_state(42)

    def test_can_get_count_player(self):
        self.assertEqual(self.info_manager.get_count_player(), 6)

    def test_can_get_player_next_action(self):
        self.info_manager.friend['1']['next_pose'] = ((1,2,3), 10)
        self.assertEqual(self.info_manager.get_player_next_aicommand(1), ((1, 2, 3), 10))

    def test_fails_get_player_next_action_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_next_aicommand(42)

    def test_fails_set_player_skill_target_goal_player_invalid(self):
        with self.assertRaises(Exception):
            action= {'skill': 'sDance', 'target': 'tDance', 'goal' : 'ball'}
            self.info_manager.set_player_skill_target_goal(42, action)

    def test_fails_set_player_skill_target_goal_action_invalid(self):
        with self.assertRaises(Exception):
            action= "invalid"
            self.info_manager.set_player_skill_target_goal(1, action)

    def test_can_set_player_tactic(self):
        self.info_manager.set_player_tactic(1, 'tDance')
        self.assertEqual(self.info_manager.tactics[1], 'tDance')

    def test_fails_set_player_tactic_invalid_player(self):
        with self.assertRaises(Exception):
            self.info_manager.set_player_tactic(42, "abc")

    def test_can_set_player_next_action(self):
        self.info_manager.set_player_next_action(1, 'action')
        self.assertEqual(self.info_manager.friend['1']['next_pose'], 'action')

    def test_can_get_ball_position(self):
        position = Position(2,2,2)
        self.info_manager.ball['position'] = position
        self.assertEqual(self.info_manager.get_ball_position(), position)

    def test_can_get_next_state(self):
        # ToDo : function actually returns hard coded-value
        self.assertEqual(self.info_manager.get_next_state(), 'debug')

    def test_can_get_next_play(self):
        # ToDo : function actually returns hard coded-value
        self.assertEqual(self.info_manager.get_next_play(1), 'pTestBench')

    def test_get_prev_player_position_index_zero(self):
        try:
            self.info_manager.get_prev_player_position(0)
        except KeyError:
            self.fail("La méthode peut calculer un index négatif.")

        self.assertEqual(self.info_manager.get_prev_player_position(0),
                         self.info_manager.get_player_position(5))


if __name__ == '__main__':
    unittest.main()

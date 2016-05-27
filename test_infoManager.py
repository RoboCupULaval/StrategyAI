# Under MIT License, see LICENSE.txt
import unittest
from UltimateStrat.InfoManager import InfoManager
from RULEngine.Game import Ball, Field, Team, Player
from RULEngine.Util.Position import Position


__author__ = 'RoboCupULaval'


class TestInfoManager(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        # ToDo : Complete refactor of infoManager/Blackboard
        ball = Ball.Ball()
        self.field = Field.Field(ball)

        blue_players = []
        yellow_players = []
        for i in range(6):
            bPlayer = Player.Player(i)
            yPlayer = Player.Player(i)
            blue_players.append(bPlayer)
            yellow_players.append(yPlayer)
        blue_team = Team.Team(blue_players, False)
        yellow_team = Team.Team(yellow_players, True)

        self.info_manager = InfoManager(self.field, blue_team, yellow_team)

        # Simpler nomenclature for readability
        self.blackboard = self.info_manager.black_board


    def test_can_get_current_play(self):
        self.blackboard['game']['play'] = "awesomePlay!"
        self.assertEqual(self.info_manager.get_current_play(), "awesomePlay!")

    def test_can_get_current_play_sequence(self):
        self.blackboard['game']['sequence'] = [1,2,3,4]
        self.assertEqual(self.info_manager.get_current_play_sequence(), [1,2,3,4])

    def test_can_set_play(self):
        self.info_manager.set_play('pDance')
        self.assertEqual(self.blackboard['game']['play'], 'pDance')

    def test_can_init_play_sequence(self):
        self.info_manager.init_play_sequence()
        self.assertEqual(self.blackboard['game']['sequence'], 0)

    def test_can_increase_play_sequence(self):
        self.info_manager.init_play_sequence()
        self.info_manager.inc_play_sequence()
        self.assertEqual(self.blackboard['game']['sequence'], 1)
        self.info_manager.inc_play_sequence()
        self.assertEqual(self.blackboard['game']['sequence'], 2)

    def test_can_get_player_target(self):
        # ToDo : Determine what is a target, tested with dummy value
        self.blackboard['friend']['1']['target'] = "Score"
        self.assertEqual(self.info_manager.get_player_target(1), 'Score')

    def test_fails_get_player_target_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_target(42)

    def test_can_get_player_goal(self):
        # ToDo : Determine what is a target, tested with dummy value
        self.blackboard['friend']['1']['goal'] = "Score more!"
        self.assertEqual(self.info_manager.get_player_goal(1), 'Score more!')

    def test_fails_get_player_goal_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_goal(42)

    def test_can_get_player_skill(self):
        self.blackboard['friend']['1']['skill'] = "AttackLeft"
        self.assertEqual(self.info_manager.get_player_skill(1), 'AttackLeft')

    def test_fails_get_player_skill_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_skill(42)

    def test_can_get_player_tactic(self):
        self.blackboard['friend']['1']['tactic'] = "Kick Properly"
        self.assertEqual(self.info_manager.get_player_tactic(1), 'Kick Properly')

    def test_fails_get_player_tactic_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_tactic(42)

    def test_can_get_player_position(self):
        self.blackboard['friend']['1']['position'] = (1, 2, 3)
        self.assertEqual(self.info_manager.get_player_position(1), (1, 2, 3))

    def test_fails_get_player_position_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_position(42)

    def test_can_get_player_pose(self):
        self.blackboard['friend']['1']['pose'] = ((1, 2, 3), 10.0)
        self.assertEqual(self.info_manager.get_player_pose(1), ((1, 2, 3), 10.0))

    def test_fails_get_player_pose_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_pose(42)

    def test_can_get_player_orientation(self):
        self.blackboard['friend']['1']['orientation'] = 10.0
        self.assertEqual(self.info_manager.get_player_orientation(1), 10.0)

    def test_fails_get_player_orientation_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_orientation(42)

    def test_can_get_player_kick_state(self):
        self.blackboard['friend']['1']['kick'] = True
        self.assertEqual(self.info_manager.get_player_kick_state(1), True)

    def test_fails_get_player_kick_state_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_kick_state(42)

    def test_can_get_count_player(self):
        self.assertEqual(self.info_manager.get_count_player(), 6)

    def test_can_get_player_next_action(self):
        self.blackboard['friend']['1']['next_pose'] = ((1,2,3), 10)
        self.assertEqual(self.info_manager.get_player_next_action(1), ((1,2,3), 10))

    def test_fails_get_player_next_action_player_invalid(self):
        with self.assertRaises(Exception):
            self.info_manager.get_player_next_action(42)

    def test_can_set_player_skill_target_goal(self):
        action= {'skill': 'sDance', 'target': 'tDance', 'goal' : 'ball'}
        self.info_manager.set_player_skill_target_goal(1, action)
        self.assertEqual(self.blackboard['friend']['1']['skill'], 'sDance')
        self.assertEqual(self.blackboard['friend']['1']['target'], 'tDance')
        self.assertEqual(self.blackboard['friend']['1']['goal'], 'ball')

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
        self.assertEqual(self.blackboard['friend']['1']['tactic'], 'tDance')

    def test_fails_set_player_tactic_invalid_player(self):
        with self.assertRaises(Exception):
            self.info_manager.set_player_tactic(42, "abc")

    def test_can_set_player_next_action(self):
        self.info_manager.set_player_next_action(1, 'action')
        self.assertEqual(self.blackboard['friend']['1']['next_pose'], 'action')

    def test_can_get_ball_position(self):
        position = Position(2,2,2)
        self.blackboard['ball']['position'] = position
        self.assertEqual(self.info_manager.get_ball_position(), position)

    def test_can_get_next_state(self):
        # ToDo : function actually returns hard coded-value
        self.assertEqual(self.info_manager.get_next_state(), 'debug')

    def test_can_get_next_play(self):
        # ToDo : function actually returns hard coded-value
        self.assertEqual(self.info_manager.get_next_play(1), 'pTestBench')


    # def test_get_speed(self):
    #     self.fail()
    #
    # def test_get_speed_ball(self):
    #    self.fail()

if __name__ == '__main__':
    unittest.main()
import unittest

from RULEngine.Util.kalman_filter.enemy_kalman_filter import EnemyKalmanFilter
from config.config_service import ConfigService
from RULEngine.Game.Player import Player
from RULEngine.Game.Team import Team
from RULEngine.Util.constant import PLAYER_PER_TEAM, MAX_PLAYER_ON_FIELD_PER_TEAM
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.team_color_service import TeamColor

class TestPlayer(unittest.TestCase):

    def setUp(self):
        ConfigService().load_file("config/sim_kalman_redirect.cfg")
        self.team = Team(TeamColor.BLUE)
        self.player1 = Player(self.team, 1)
        self.player2 = Player(self.team, 2)

    def test_init_normal(self):
        p = Player(self.team, 0)
        self.assertIsNone(p.cmd)
        self.assertIsNotNone(p)
        self.assertIsNotNone(p.team)
        self.assertIsNotNone(p.id)
        self.assertIsNotNone(p.pose)
        self.assertEqual(p.pose, Pose())
        self.assertIsNotNone(p.velocity)
        self.assertEqual(p.velocity, Pose())
        self.assertIsNotNone(p.kf)
        self.assertTrue(isinstance(p.kf, EnemyKalmanFilter))
        self.assertIsNotNone(p.update)
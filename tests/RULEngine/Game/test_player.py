import unittest

from RULEngine.Util.Pose import Pose
from RULEngine.Util.kalman_filter.enemy_kalman_filter import EnemyKalmanFilter

from RULEngine.services.team_color_service import TeamColor
from Util import Position
from ai.GameDomainObjects import Player
from ai.GameDomainObjects import Team


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.team = Team(TeamColor.BLUE)
        self.player1 = Player(self.team, 1)
        self.player2 = Player(self.team, 2)

    def test_init_normal(self):
        random_player_id = 0
        p = Player(self.team, random_player_id)
        self.assertIsNotNone(p)
        self.assertIsNotNone(p.id)
        self.assertEqual(random_player_id, p.id)
        self.assertIsNotNone(p.team)
        self.assertIsNotNone(p.pose)
        self.assertEqual(p.pose, Pose())
        self.assertIsNotNone(p.velocity)
        self.assertEqual(p.velocity, Pose())
        self.assertIsNotNone(p.kf)
        self.assertTrue(isinstance(p.kf, EnemyKalmanFilter))
        self.assertIsNotNone(p.update)

    def test_has_id(self):
        player_id = 0
        p = Player(self.team, player_id)
        self.assertTrue(p.has_id(0))
        for i in range(1, 13):
            self.assertFalse(p.has_id(i))

    def test_check_if_on_field(self):
        # needs to fails since the pose is the default one
        self.assertFalse(self.player1.check_if_on_field())
        self.player1.pose = Pose(Position(200, 200), 1)
        self.assertTrue(self.player1.check_if_on_field())

    def test__update(self):
        self.player1._update(Pose(Position(200, 200), 1))
        self.assertEqual(self.player1.pose, Pose(Position(200, 200), 1))
        self.assertNotEqual(self.player1.pose, Pose())

    def test__kalman_update(self):
        self.assertEqual(self.player1.pose, Pose())
        # one kalman update and the kalman filter will put the pose of the player to Pose(9999, 9999, 0) or something
        self.player1._kalman_update([None], 0.5)
        self.assertNotEqual(self.player1.pose, Pose())
        self.assertNotEqual(self.player1.pose, Pose(200, 200, 1))
        # send enough image where the robot has no position for the kalman to say the robot
        # isnt on the field with Pose()
        for i in range(21):
            self.player1._kalman_update([None], 0.5)
        self.assertEqual(self.player1.pose, Pose())

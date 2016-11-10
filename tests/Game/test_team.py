import unittest

from RULEngine.Game.Player import Player
from RULEngine.Game.Team import Team
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose


class TestTeam(unittest.TestCase):

    def setUp(self):
        self.team = Team(True)
        self.first_player = self.team.players[0]
        self.second_player = self.team.players[1]
        self.no_player = Player(self.team, 0)

    def test_init(self):
        self.assertEqual(PLAYER_PER_TEAM, len(self.team.players))
        self.assertEqual(0, self.team.score)
        self.assertEqual(True, self.team.is_team_yellow)

    def test_has_player_exists(self):
        self.assertTrue(self.team.has_player(self.first_player))

    def test_has_player_no_exists(self):
        self.assertFalse(self.team.has_player(self.no_player))

    def test_move_and_rotate(self):
        init_pose = self.first_player.pose
        self.assertEqual(init_pose, self.team.players[0].pose)
        self.team.move_and_rotate_player(0, Pose(Position(500, 500)))
        self.assertNotEqual(init_pose, self.team.players[0].pose)
        self.assertEqual(self.team.players[0].pose, self.first_player.pose)

    def test_move_and_rotate_invalid_id(self):
        uut = self.team.move_and_rotate_player
        self.assertRaises(KeyError, uut, 10, Pose())

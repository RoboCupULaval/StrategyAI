import unittest

from RULEngine.Game.Player import Player
from RULEngine.Game.Team import Team
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.team_color_service import TeamColor


class TestTeam(unittest.TestCase):

    def setUp(self):
        self.team = Team(TeamColor.YELLOW)
        self.team_blue = Team(TeamColor.BLUE)
        self.first_player = self.team.players[0]
        self.second_player = self.team.players[1]
        self.no_player = Player(self.team, 0)

    def test_init(self):
        self.assertEqual(PLAYER_PER_TEAM, len(self.team.players))
        self.assertEqual(0, self.team.score)
        self.assertEqual(TeamColor.YELLOW, self.team.team_color)

    def test_has_player_exists(self):
        self.assertTrue(self.team.has_player(self.first_player))

    def test_has_player_no_exists(self):
        self.assertFalse(self.team.has_player(self.no_player))

    def test_update_player(self):
        init_pose = self.first_player.pose
        self.assertEqual(init_pose, self.team.players[0].pose)
        self.team.update_player(0, Pose(Position(500, 500)), 0)
        self.assertNotEqual(init_pose, self.team.players[0].pose)
        self.assertEqual(self.team.players[0].pose, self.first_player.pose)

    def test_invalid_id(self):
        uut = self.team.update_player
        self.assertRaises(KeyError, uut, 10, Pose())

    def test_is_team_yellow(self):
        self.assertTrue(self.team.is_team_yellow())
        self.assertFalse(self.team_blue.is_team_yellow())

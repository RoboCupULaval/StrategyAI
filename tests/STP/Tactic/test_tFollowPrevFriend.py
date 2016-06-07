# Under MIT License, see LICENSE.txt
from unittest import TestCase

from RULEngine.Game.Field import Field
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Team import Team
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose, Position

from ai.STP.Tactic.tFollowPrevFriend import tFollowPrevFriend
from ai.InfoManager import InfoManager

__author__ = 'RoboCupULaval'


class TestTacticFollowPrevFriend(TestCase):
    """ Tests de la classe tFollowPrevFriend """
    def setUp(self):
        self.tactic = tFollowPrevFriend()

        # Initialisation de l'InfoManager avec des équipes de robots et une balle
        self.team = Team([Player(bot_id) for bot_id in range(6)], True)
        for player in self.team.players:
            self.team.players[player.id].position = Position(100 * player.id, 100 * player.id)

        self.op_team = Team([Player(bot_id) for bot_id in range(6)], False)
        for player in self.op_team.players:
            self.op_team.players[player.id].position = Position(-100 * player.id - 100, -100 * player.id - 100)

        self.field = Field(Ball())
        self.field.ball.set_position(Position(1000, 0), 1)
        self.info = InfoManager(self.field, self.team, self.op_team)

    def test_construction(self):
        self.assertNotEqual(self.tactic, None)
        self.assertIsInstance(self.tactic, tFollowPrevFriend)

    def test_name(self):
        self.assertEqual(self.tactic.name, tFollowPrevFriend.__name__)

    def test_if_ball_is_far(self):
        result = self.tactic.apply(self.info, 0)
        bot_pst = self.info.get_player_position(0)
        player_pst = self.info.get_prev_player_position(0)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        expect = {'skill': 'sGoToTarget', 'target': player_pst, 'goal': bot_pst}
        print("Expected\n" + str(expect))
        print("Result\n" + str(result))
        self.assertEqual(result, expect)

    def test_if_ball_is_too_near(self):
        # Changement de la position de la balle pour la mettre proche du robot 0
        self.info.black_board.bb['ball']['position'] = Position(50, 50)

        result = self.tactic.apply(self.info, 0)
        bot_pst = self.info.get_player_position(0)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'skill': 'sGoToTarget', 'target': bot_pst, 'goal': bot_pst})

# Under MIT License, see LICENSE.txt
from unittest import TestCase

from RULEngine.Game.Field import Field
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Team import Team
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Framework import GameState

from ai.STP.Tactic.tPath import tPath
from ai.InfoManager import InfoManager

__author__ = 'RoboCupULaval'


class TestTacticStop(TestCase):
    """ Tests de la classe tPath """
    def setUp(self):
        self.tactic = tPath()

        # Initialisation de l'InfoManager avec des équipes de robots et une balle
        self.team = Team(True)
        for player in self.team.players:
            self.team.players[player.id].position = Position(100 * player.id, 100 * player.id)

        self.op_team = Team(False)
        for player in self.op_team.players:
            self.op_team.players[player.id].position = Position(-100 * player.id - 100, -100 * player.id - 100)

        self.field = Field(Ball())
        self.field.ball.set_position(Position(1000, 0), 1)
        self.info = InfoManager()

        game_state = GameState(self.field, None, self.team, self.op_team, {})
        self.info.update(game_state)

    def test_construction(self):
        self.assertNotEqual(self.tactic, None)
        self.assertIsInstance(self.tactic, tPath)

    def test_name(self):
        self.assertEqual(self.tactic.name, tPath.__name__)

    def test_if_next_action_is_pose(self):
        self.info.friend['0']['next_pose'] = Pose(Position(2000, 0), 0)
        result = self.tactic.apply(self.info, 0)
        ball_pst = self.info.get_ball_position()

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'skill': 'sGeneratePath', 'target': ball_pst, 'goal': ball_pst})

    def test_if_next_action_is_list_of_pose(self):
        self.info.friend['0']['next_pose'] = [Pose(Position(2000, 0), 0), Pose(Position(0, 2000), 0)]
        result = self.tactic.apply(self.info, 0)
        ball_pst = self.info.get_ball_position()

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'skill': 'sWait', 'target': ball_pst, 'goal': ball_pst})

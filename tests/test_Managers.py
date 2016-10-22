# Under MIT License, see LICENSE.txt
import unittest

from RULEngine.Framework import GameState
from RULEngine.Game import Ball, Team, Field, Referee
from RULEngine.Util import Pose, Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.states.game_state import GameState
from ai.states.module_state import ModuleState


class TestGameStateManager(unittest.TestCase):
    """
        Teste les différentes fonctionnalités du GameStateManager
    """
    def setUp(self):
        self.field = Field.Field(Ball.Ball())
        self.my_team = Team.Team(True)
        self.other_team = Team.Team(False)
        self.GameStateManager1 = GameState()
        self.GameStateManager2 = GameState()

    def test_singleton(self):
        """
            Teste si le Manager est un singleton,
             i.e. s'il ne peut y avoir qu'une seule instance du manager
        """
        self.assertTrue(self.GameStateManager1 is self.GameStateManager2)

    def test_update_ball_position(self):
        new_ball_position = Position.Position(1500, 1500, 0)
        self.GameStateManager2._update_ball_position(new_ball_position)
        self.assertEqual(new_ball_position, self.GameStateManager1.get_ball_position())

    def test_update_field(self):
        new_ball_position = Position.Position(2500, 2500, 0)
        self.field.move_ball(new_ball_position, 5)
        self.GameStateManager2._update_field(self.field)
        self.assertEqual(self.GameStateManager1.get_ball_position(), new_ball_position)

    def test_update_player(self):
        new_player_pose = Pose.Pose(Position.Position(1700, 1700, 0), 25)
        self.GameStateManager2._update_player(3, new_player_pose, True)
        self.assertEqual(new_player_pose, self.GameStateManager1.get_player_pose(3, True))
        self.GameStateManager2._update_player(3, new_player_pose, False)
        self.assertEqual(new_player_pose, self.GameStateManager1.get_player_pose(3, False))

    def test_update_team(self):
        new_player_pose = Pose.Pose(Position.Position(1000, 1000, 0), 25)
        for i in range(PLAYER_PER_TEAM):
            self.my_team.move_and_rotate_player(i, new_player_pose)
            new_player_pose.position += 200
        self.GameStateManager2._update_team(self.my_team, True)
        for i in range(PLAYER_PER_TEAM):
            self.assertEqual(self.GameStateManager1.get_player_pose(i, True), self.my_team.players[i].pose)

        new_player_pose = Pose.Pose(Position.Position(1000, 1000, 0), 25)
        for i in range(PLAYER_PER_TEAM):
            self.other_team.move_and_rotate_player(i, new_player_pose)
            new_player_pose.position += 100
        self.GameStateManager2._update_team(self.other_team, False)
        for i in range(PLAYER_PER_TEAM):
            self.assertEqual(self.GameStateManager1.get_player_pose(i, False), self.other_team.players[i].pose)

    def test_update_timestamp(self):
        new_timestamp = 123.25
        self.GameStateManager2._update_timestamp(new_timestamp)
        self.assertEqual(self.GameStateManager1.timestamp, new_timestamp)

    def test_update(self):
        new_timestamp = 145.36
        new_ball_position = Position.Position(500, 500, 0)
        self.field.move_ball(new_ball_position, 5)

        new_player_pose = Pose.Pose(Position.Position(1000, 1000, 0), 25)
        for i in range(PLAYER_PER_TEAM):
            self.my_team.move_and_rotate_player(i, new_player_pose)
            new_player_pose.position += 200

        new_player_pose = Pose.Pose(Position.Position(1000, 1000, 0), 25)
        for i in range(PLAYER_PER_TEAM):
            self.other_team.move_and_rotate_player(i, new_player_pose)
            new_player_pose.position += 100

        new_game_state = GameState(
            field=self.field,
            referee=Referee.Referee(),
            friends=self.my_team,
            enemies=self.other_team,
            timestamp=new_timestamp,
            debug='Test'
        )

        self.GameStateManager2.update(new_game_state)
        self.assertEqual(new_game_state.field.ball.position, self.GameStateManager1.get_ball_position())
        for i in range(PLAYER_PER_TEAM):
            self.assertEqual(self.GameStateManager1.get_player_pose(i, False), self.other_team.players[i].pose)
            self.assertEqual(self.GameStateManager1.get_player_pose(i, False), self.other_team.players[i].pose)
        self.assertEqual(new_game_state.timestamp, self.GameStateManager1.timestamp)


class TestModuleManager(unittest.TestCase):
    """
        Teste les différentes fonctionnalités du ModuleManager
    """
    def setUp(self):
        self.ModuleManager1 = ModuleState()
        self.ModuleManager2 = ModuleState()

    def test_singleton(self):
        """
            Teste si le Manager est un singleton,
             i.e. s'il ne peut y avoir qu'une seule instance du manager
        """
        self.assertTrue(self.ModuleManager1 is self.ModuleManager2)

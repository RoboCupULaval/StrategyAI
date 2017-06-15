import unittest
import numpy as np

from unittest.mock import MagicMock, patch, create_autospec
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Game.Player import Player
from RULEngine.Game.Team import Team
from ai.states.game_state import GameState
from ai.Algorithm.evaluation_module import best_passing_option, line_of_sight_clearance, trajectory_score


class TestEvaluationModule(unittest.TestCase):
    MULTIPLICATIVE_NULL_VALUE = 1
    ADDITIVE_NULL_VALUE = 0
    MAX_VALUE = 15

    def setUp(self):
        self.pointA = Position(0,0)
        self.pointB = Position(0,0)
        self.obstacle = Position(0,0)

    def test_givenObstacleBehindPlayer_thenReturnsMultiplicativeNullValue(self):
        self._define_points_obstacle((100,100), (200,200), (50,50))

        assert trajectory_score(self.pointA, self.pointB, self.obstacle) == self.MULTIPLICATIVE_NULL_VALUE

    def test_givenObstacleVeryFarFromPlayer_thenTrajectoryScoreReturnsMultiplicativeNullValue(self):
        self._define_points_obstacle((100,100), (200,200), (1500,1500))

        assert trajectory_score(self.pointA, self.pointB, self.obstacle) == self.MULTIPLICATIVE_NULL_VALUE

    def test_givenObstacleOnPath_thenTrajectoryScoreReturnsMaxValue(self):
        self._define_points_obstacle((100,100),(200,200),(150,150))

        assert trajectory_score(self.pointA, self.pointB, self.obstacle) == self.MAX_VALUE


    def test_givenOnePlayerInMyTeamFarFromGoal_thenLineOfSightClearanceIsOne(self):
        player1 = create_autospec(Player)
        pose1 = create_autospec(Pose)
        pose1.position = Position(100,100)
        player1.pose = pose1
        player1.id = 1

        player2 = create_autospec(Player)
        pose2 = create_autospec(Pose)
        pose2.position = Position(1500,1500)
        player2.pose = pose2
        player2.id = 2


        team1 = create_autospec(Team)
        team1.available_players = {1:player1, 2:player2}
        team2 = create_autospec(Team)
        team2.available_players = {}


        GameState().my_team = team1
        GameState().other_team= team2
        self.obstacle.x, self.obstacle.y = (200,200)

        expected_score = np.linalg.norm(player1.pose.position - self.obstacle)

        assert line_of_sight_clearance(player1, self.obstacle) == expected_score



    def _define_points_obstacle(self, pointA, pointB, obstacle):
        self.pointA.x, self.pointA.y = pointA
        self.pointB.x, self.pointB.y = pointB
        self.obstacle.x, self.obstacle.y = obstacle
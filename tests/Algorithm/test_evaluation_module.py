
import unittest
from unittest.mock import create_autospec

from Util import Pose, Position

from ai.Algorithm.evaluation_module import trajectory_score
from ai.GameDomainObjects import Player
from ai.GameDomainObjects import Team
from ai.states.game_state import GameState


class TestEvaluationModule(unittest.TestCase):
    MULTIPLICATIVE_NULL_VALUE = 1
    ADDITIVE_NULL_VALUE = 0
    MAX_VALUE = 15

    def setUp(self):
        self.start_point = Position(0, 0)
        self.goal = Position(0, 0)
        self.obstacle = Position(0, 0)

    def test_givenObstacleBehindPlayer_thenReturnsMultiplicativeNullValue(self):
        self._define_points_obstacle((100, 100), (200, 200), (50, 50))

        assert trajectory_score(self.start_point, self.goal, self.obstacle) == self.MULTIPLICATIVE_NULL_VALUE

    def test_givenObstacleVeryFarFromPlayer_thenTrajectoryScoreReturnsMultiplicativeNullValue(self):
        self._define_points_obstacle((100, 100), (200, 200), (1500, 1500))

        assert trajectory_score(self.start_point, self.goal, self.obstacle) == self.MULTIPLICATIVE_NULL_VALUE

    def test_givenObstacleOnPath_thenTrajectoryScoreReturnsMaxValue(self):
        self._define_points_obstacle((100, 100), (200, 200), (150, 150))

        assert trajectory_score(self.start_point, self.goal, self.obstacle) == self.MAX_VALUE

    def _define_points_obstacle(self, start_point, goal, obstacle):
        self.start_point.x, self.start_point.y = start_point
        self.goal.x, self.goal.y = goal
        self.obstacle.x, self.obstacle.y = obstacle
     
        
def build_mock_player(position, pid):
    player = create_autospec(Player)
    pose = create_autospec(Pose)
    pose.position = position
    player.pose = pose
    player.id = pid
    return player


def create_mock_teams(allies, opponents):
    team1 = create_autospec(Team)
    team1.available_players = allies
    GameState()._our_team = team1
    print(GameState().our_team.available_players.values())

    team2 = create_autospec(Team)
    team2.available_players = opponents
    GameState()._enemy_team = team2

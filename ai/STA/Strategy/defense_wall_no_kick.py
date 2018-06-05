# Under MIT license, see LICENSE.txt
from Util.constant import KEEPOUT_DISTANCE_FROM_BALL
from ai.Algorithm.path_partitionner import Obstacle
from ai.STA.Strategy.defense_wall import DefenseWall
from ai.states.game_state import GameState


# noinspection
class DefenseWallNoKick(DefenseWall):
    def __init__(self, game_state: GameState):
        super().__init__(game_state, can_kick=False, stay_away_from_ball=True)

    def obstacles(self):
        return [Obstacle(self.game_state.ball_position.array, avoid_distance=KEEPOUT_DISTANCE_FROM_BALL)]
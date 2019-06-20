# Under MIT license, see LICENSE.txt
from Util.constant import KEEPOUT_DISTANCE_FROM_BALL
from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall


# noinspection PyTypeChecker
class StayAway(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for r, p in self.assigned_roles.items():
            if r == Role.GOALKEEPER:
                # If the ball is at the perimeter of the goal, we don't want to have the goalkeeper move out of the goal
                keepout_radius = KEEPOUT_DISTANCE_FROM_BALL / 2
                self.create_node(r, StayAwayFromBall(self.game_state, p, keepout_radius=keepout_radius, forbidden_areas=[]))
            else:
                self.create_node(r, StayAwayFromBall(self.game_state, p))

    @classmethod
    def required_roles(cls):
        return []

    @classmethod
    def optional_roles(cls):
        return [r for r in Role]
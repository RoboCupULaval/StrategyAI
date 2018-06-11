# Under MIT license, see LICENSE.txt
import logging

from Util import Pose
from Util.constant import KEEPOUT_DISTANCE_FROM_BALL
from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.place_ball import PlaceBall
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall


# noinspection PyTypeChecker
class BallPlacement(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        target = None
        if self.game_state.last_ref_state is None:
            self.logger.warning("The AI has not received a referee message and does not know where to place the ball.")
        else:
            target = self.game_state.last_ref_state.ball_placement_position
            if target is None:
                self.logger.warning("The last ref_state did not contains a ball_placement position\n"
                                    "The AI does not know where to place the ball")
        for r, p in self.assigned_roles.items():
            if r == Role.FIRST_ATTACK and target is not None:
                self.create_node(r, PlaceBall(self.game_state, p, target=Pose(target)))
            else:
                self.create_node(r, StayAwayFromBall(self.game_state, p, keepout_radius=2*KEEPOUT_DISTANCE_FROM_BALL))

    @classmethod
    def required_roles(cls):
        return [Role.FIRST_ATTACK]

    @classmethod
    def optional_roles(cls):
        return [r for r in Role if r != Role.FIRST_ATTACK]
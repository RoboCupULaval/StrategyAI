# Under MIT license, see LICENSE.txt

from Util import Role
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall


class StayAway(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        for r in Role:
            p = self.game_state.get_player_by_role(r)
            if p:
                self.add_tactic(r, StayAwayFromBall(self.game_state, p))
# Under MIT license, see LICENSE.txt

from Util.role import Role
from Util.role_mapping_rule import KeepPrevMappingOtherwiseRandom
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall


# noinspection PyTypeChecker
class StayAway(Strategy):
    def __init__(self, p_game_state, assigned_roles):
        super().__init__(p_game_state)

        for r, p in assigned_roles.items():
            self.add_tactic(r, StayAwayFromBall(self.game_state, p))

    @classmethod
    def required_roles(cls):
        return {}

    @classmethod
    def optional_roles(cls):
        return {r: KeepPrevMappingOtherwiseRandom for r in Role}
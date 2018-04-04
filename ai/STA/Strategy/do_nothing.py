# Under MIT License, see LICENSE.txt
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.stop import Stop


# noinspection PyTypeChecker
class DoNothing(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        for r, p in self.assigned_roles.items():
            self.create_node(r, Stop(self.game_state, p))

    @classmethod
    def required_roles(cls):
        return {}

    @classmethod
    def optional_roles(cls):
        return {r: keep_prev_mapping for r in Role}

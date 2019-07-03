# Under MIT License, see LICENSE.txt

from Util.role import Role
from ai.STA.Strategy.graphless_strategy import GraphlessStrategy
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.test_best_passing_option import TestBestPassingOption


class TestPassingOptions(GraphlessStrategy):

    def __init__(self, p_game_state, can_kick_in_goal=True):
        super().__init__(p_game_state)

        # self.logger.debug(self.assigned_roles.items())
        for r, p in self.assigned_roles.items():
            if r == Role.FIRST_ATTACK:
                self.roles_to_tactics[r] = TestBestPassingOption(self.game_state, p,
                                                                 can_kick_in_goal=can_kick_in_goal)
            else:
                self.roles_to_tactics[r] = Stop(self.game_state, p)
        self.logger.debug(self.roles_to_tactics.items())
        self.next_state = self.do_nothing

    def do_nothing(self):
        pass

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_DEFENCE,
                Role.MIDDLE,
                Role.SECOND_ATTACK,
                Role.FIRST_ATTACK,
                Role.SECOND_DEFENCE
                ]

    @classmethod
    def optional_roles(cls):
        return []

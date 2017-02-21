# Under MIT License, see LICENSE.txt
from ai.STA.Tactic.test_turn_on_you import TestTurnOnYou
from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.Algorithm.Node import Node
# TODO change the way we access no player
from RULEngine.Util.constant import PLAYER_PER_TEAM


class DoNothing(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for i in range(PLAYER_PER_TEAM):
            self.add_tactic(i, TestTurnOnYou(self.game_state, i))

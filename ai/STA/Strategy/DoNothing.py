# Under MIT License, see LICENSE.txt

from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop
from ai.Algorithm.Node import Node
# TODO change the way we access no player
from RULEngine.Util.constant import PLAYER_PER_TEAM


class DoNothing(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for i in range(PLAYER_PER_TEAM):
            self.graphs[i].add_node(Node(Stop(self.game_state, i)))

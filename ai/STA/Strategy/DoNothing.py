from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop
from ai.Algorithm.Node import Node
from RULEngine.Util.constant import PLAYER_PER_TEAM


class DoNothing(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager)
        for i in range(PLAYER_PER_TEAM):
            self.graphs[i].add_node(Node(Stop(self.info_manager, i)))

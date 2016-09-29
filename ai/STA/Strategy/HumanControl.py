# Under MIT license, see LICENSE.txt

from . Strategy import Strategy
from ai.Algorithm.Node import Node
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.Stop import Stop
from RULEngine.Util.constant import PLAYER_PER_TEAM


class HumanControl(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager)
        for i in range(PLAYER_PER_TEAM):
            self.graphs[i].add_node(Node(Stop(self.info_manager, i)))

    def assign_tactic(self, tactic, robot_id):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)
        assert 0 <= robot_id < PLAYER_PER_TEAM

        self.graphs[robot_id].remove_node(0)
        self.graphs[robot_id].add_node(Node(tactic))

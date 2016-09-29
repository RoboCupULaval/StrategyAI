# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.CoverZone import CoverZone
from . Strategy import Strategy
from ai.Algorithm.Node import Node

# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire


class SimpleOffense(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager)

        self.graphs[0].add_node(Node(GoalKeeper(self.info_manager, 0)))
        for i in range(1, 6):
            self.graphs[i].add_node(Node(GoGetBall(self.info_manager, i)))

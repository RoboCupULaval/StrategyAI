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


class SimpleDefense(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager)

        self.graphs[0].add_node(Node(GoalKeeper(self.info_manager, 0)))
        self.graphs[1].add_node(Node(GoGetBall(self.info_manager, 1)))
        self.graphs[2].add_node(Node(CoverZone(self.info_manager, 2, FIELD_Y_TOP, 0, FIELD_X_LEFT, FIELD_X_LEFT / 2)))
        self.graphs[3].add_node(Node(CoverZone(self.info_manager, 3, 0, FIELD_Y_BOTTOM, FIELD_X_LEFT, FIELD_X_LEFT / 2)))
        self.graphs[4].add_node(Node(CoverZone(self.info_manager, 4, FIELD_Y_TOP, 0, FIELD_X_LEFT / 2, 0)))
        self.graphs[5].add_node(Node(CoverZone(self.info_manager, 5, 0, FIELD_Y_BOTTOM, FIELD_X_LEFT / 2, 0)))

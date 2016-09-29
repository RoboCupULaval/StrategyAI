# Under MIT license, see LICENSE.txt

from math import pi
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import *

__author__ = 'RoboCupULaval'


class TestTransitions(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager)

        self.graphs[0].add_node(Node(GoalKeeper(self.info_manager, 0)))
        self.graphs[1].add_node(Node(GoToPosition(self.info_manager, 1, Pose(Position(), 3*pi/2))))
        self.graphs[1].add_node(Node(GoToPosition(self.info_manager, 1, Pose(Position(500, 0), 0))))
        self.graphs[1].add_node(Node(GoToPosition(self.info_manager, 1, Pose(Position(500, 500), pi/2))))
        self.graphs[1].add_node(Node(GoToPosition(self.info_manager, 1, Pose(Position(0, 500), pi))))
        self.graphs[1].add_vertex(0, 1, self.condition)
        self.graphs[1].add_vertex(1, 2, self.condition)
        self.graphs[1].add_vertex(2, 3, self.condition)
        self.graphs[1].add_vertex(3, 0, self.condition)

        for i in range(2, PLAYER_PER_TEAM):
            self.graphs[i].add_node(Node(Stop(self.info_manager, i)))

    def condition(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[1].get_current_tactic().status_flag == SUCCESS

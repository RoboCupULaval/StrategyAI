# Under MIT license, see LICENSE.txt

from math import pi
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.GoStraightTo import GoStraightTo
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import *

__author__ = 'RoboCupULaval'


class chTest(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robot_id = 4
        self.add_tactic(robot_id, GoStraightTo(self.game_state, robot_id, Pose(Position(0, 1500), pi)))
        self.add_tactic(robot_id, GoStraightTo(self.game_state, robot_id, Pose(Position(1500, 1500), pi)))
        self.add_condition(robot_id,0,1,self.condition)
        self.add_condition(robot_id,1,0,self.condition)

        # noeuds vides
        self.graphs[0].add_node(Node(Stop(self.game_state, 0)))
        self.graphs[1].add_node(Node(Stop(self.game_state, 0)))
        self.graphs[2].add_node(Node(Stop(self.game_state, 0)))
        self.graphs[3].add_node(Node(Stop(self.game_state, 0)))
        self.graphs[5].add_node(Node(Stop(self.game_state, 0)))

    def condition(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[4].get_current_tactic().status_flag == Flags.SUCCESS

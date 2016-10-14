# Under MIT License, see LICENSE.txt

from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoStraightTo import GoStraightTo
from ai.STA.Tactic.Stop import Stop
from RULEngine.Util.Pose import Position, Pose
from ai.STA.Tactic.tactic_constants import *


class WeirdmovementStrategy(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.graphs[0].add_node(Node(Stop(self.game_state, 0)))
        self.graphs[0].add_node(Node(GoStraightTo(self.game_state, 0, Pose(Position(-500, -500)))))
        self.graphs[0].add_node(Node(GoStraightTo(self.game_state, 0, Pose(Position(-1500, -1500)))))
        self.graphs[0].add_vertex(0, 1, self.condition)
        self.graphs[0].add_vertex(1, 2, self.condition)
        self.graphs[0].add_vertex(2, 0, self.condition)

        self.graphs[1].add_node(Node(GoStraightTo(self.game_state, 1, Pose(Position(0, 0)))))
        self.graphs[1].add_node(Node(GoStraightTo(self.game_state, 1, Pose(Position(1000, 0)))))
        self.graphs[1].add_node(Node(GoStraightTo(self.game_state, 1, Pose(Position(1000, 1000)))))
        self.graphs[1].add_node(Node(GoStraightTo(self.game_state, 1, Pose(Position(0, 1000)))))
        self.graphs[1].add_vertex(0, 1, self.condition)
        self.graphs[1].add_vertex(1, 2, self.condition)
        self.graphs[1].add_vertex(2, 3, self.condition)
        self.graphs[1].add_vertex(3, 0, self.condition)

        for i in range(2, 6):
            self.graphs[i].add_node(Node(Stop(self.game_state, i)))


    def condition(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[1].get_current_tactic().status_flag == SUCCESS and \
            self.graphs[0].get_current_tactic().status_flag == SUCCESS

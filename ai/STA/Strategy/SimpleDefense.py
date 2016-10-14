# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.CoverZone import CoverZone
from . Strategy import Strategy
from ai.Algorithm.Node import Node


class SimpleDefense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.graphs[0].add_node(Node(GoalKeeper(self.game_state, 0)))
        self.graphs[1].add_node(Node(GoGetBall(self.game_state, 1)))
        self.graphs[2].add_node(Node(CoverZone(self.game_state, 2, FIELD_Y_TOP, 0, FIELD_X_LEFT, FIELD_X_LEFT / 2)))
        self.graphs[3].add_node(Node(CoverZone(self.game_state, 3, 0, FIELD_Y_BOTTOM, FIELD_X_LEFT, FIELD_X_LEFT / 2)))
        self.graphs[4].add_node(Node(CoverZone(self.game_state, 4, FIELD_Y_TOP, 0, FIELD_X_LEFT / 2, 0)))
        self.graphs[5].add_node(Node(CoverZone(self.game_state, 5, 0, FIELD_Y_BOTTOM, FIELD_X_LEFT / 2, 0)))

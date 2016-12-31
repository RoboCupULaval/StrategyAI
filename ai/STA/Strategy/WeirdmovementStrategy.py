# Under MIT License, see LICENSE.txt

from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.Stop import Stop
from RULEngine.Util.Pose import Position, Pose
from ai.STA.Tactic.tactic_constants import Flags


class WeirdmovementStrategy(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.add_tactic(0, Stop(self.game_state, 0))
        self.add_tactic(0, GoToPositionNoPathfinder(self.game_state, 0, Pose(Position(-500, -500))))
        self.add_tactic(0, GoToPositionNoPathfinder(self.game_state, 0, Pose(Position(-1500, -1500))))
        self.add_condition(0, 0, 1, self.condition2)
        self.add_condition(0, 1, 2, self.condition)
        self.add_condition(0, 2, 0, self.condition)

        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(0, 0))))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(1000, 0))))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(1000, 1000))))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(0, 1000))))
        self.add_condition(1, 0, 1, self.condition1)
        self.add_condition(1, 1, 2, self.condition1)
        self.add_condition(1, 2, 3, self.condition1)
        self.add_condition(1, 3, 0, self.condition1)

        for i in range(2, 6):
            self.add_tactic(i, Stop(self.game_state, i))

    def condition(self):
        return self.graphs[0].get_current_tactic().status_flag == Flags.SUCCESS

    def condition1(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[1].get_current_tactic().status_flag == Flags.SUCCESS

    def condition2(self):
            self.graphs[1].nodes[3].tactic.status_flag == Flags.SUCCESS

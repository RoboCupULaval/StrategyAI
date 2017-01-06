# Under MIT license, see LICENSE.txt

from math import pi
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.ProtectGoal import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags

__author__ = 'RoboCupULaval'


class TestTransitions(Strategy):
    """
    Stratégie permettant de tester les transitions dans la suite de tactiques associées à un robot.
    Robot 0: Gardien, une seule tactique.
    Robot 1: Se déplace en suivant une trajectoire carrée. Suite de 4 tactiques GoToPosition.
    Robot 2 à 5: Ne bouge pas, une seule tactique.
    """
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.add_tactic(0, GoalKeeper(self.game_state, 0))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(), 3 * pi / 2)))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(1000, 0), 0)))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(1000, 1000), pi / 2)))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(0, 1000), pi)))

        self.add_condition(1, 0, 1, self.condition)
        self.add_condition(1, 1, 2, self.condition)
        self.add_condition(1, 2, 3, self.condition)
        self.add_condition(1, 3, 0, self.condition)

        for i in range(2, PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

    def condition(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[1].get_current_tactic().status_flag == Flags.SUCCESS

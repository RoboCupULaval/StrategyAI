# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from RULEngine.Util.Pose import Position, Pose

__author__ = 'RoboCupULaval'


class PerpetualMovement(Strategy):
    """
    Stratégie permettant de tester les transitions dans la suite de tactiques associées à un robot.
    Robot 0: Gardien, une seule tactique.
    Robot 1: Se déplace en suivant une trajectoire carrée. Suite de 4 tactiques GoToPosition.
    Robot 2 à 5: Ne bouge pas, une seule tactique.
    """
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        # Robot 0
        self.add_tactic(0, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-1500, 1500))))
        self.add_tactic(0, GoToPositionPathfinder(self.game_state, 0, Pose(Position(1500, 1500))))
        self.add_tactic(0, GoToPositionPathfinder(self.game_state, 0, Pose(Position(1500, -1500))))
        self.add_tactic(0, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-1500, -1500))))

        self.add_condition(0, 0, 1, self.condition0)
        self.add_condition(0, 1, 2, self.condition0)
        self.add_condition(0, 2, 3, self.condition0)
        self.add_condition(0, 3, 1, self.condition0)

        # Robot 1
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(2000, -2000))))
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-2000, 2000))))
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(2000, 2000))))
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-2000, -2000))))

        self.add_condition(1, 0, 1, self.condition1)
        self.add_condition(1, 1, 2, self.condition1)
        self.add_condition(1, 2, 3, self.condition1)
        self.add_condition(1, 3, 1, self.condition1)

        # Robot 2
        self.add_tactic(2, GoToPositionPathfinder(self.game_state, 0, Pose(Position(0, 2100))))
        self.add_tactic(2, GoToPositionPathfinder(self.game_state, 0, Pose(Position(0, 2100))))

        self.add_condition(2, 0, 1, self.condition2)
        self.add_condition(2, 1, 0, self.condition2)

        # Robot 3
        self.add_tactic(3, GoToPositionPathfinder(self.game_state, 0, Pose(Position(2100, 0))))
        self.add_tactic(3, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-2100, 0))))

        self.add_condition(3, 0, 1, self.condition3)
        self.add_condition(3, 1, 0, self.condition3)

        self.add_tactic(4, Stop(self.game_state, 4))
        self.add_tactic(5, Stop(self.game_state, 5))

    def condition0(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[0].get_current_tactic().status_flag == Flags.SUCCESS

    def condition1(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[1].get_current_tactic().status_flag == Flags.SUCCESS

    def condition2(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[2].get_current_tactic().status_flag == Flags.SUCCESS

    def condition3(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[3].get_current_tactic().status_flag == Flags.SUCCESS

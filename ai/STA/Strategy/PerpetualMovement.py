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

        # Robot 1
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(2000, -2000))))
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-2000, 2000))))
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(2000, 2000))))
        self.add_tactic(1, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-2000, -2000))))

        # Robot 2
        self.add_tactic(2, GoToPositionPathfinder(self.game_state, 0, Pose(Position(0, 2100))))
        self.add_tactic(2, GoToPositionPathfinder(self.game_state, 0, Pose(Position(0, 2100))))

        # Robot 3
        self.add_tactic(3, GoToPositionPathfinder(self.game_state, 0, Pose(Position(2100, 0))))
        self.add_tactic(3, GoToPositionPathfinder(self.game_state, 0, Pose(Position(-2100, 0))))

        for i in range(0, 1):
            self.add_condition(i, 0, 1, self.condition)
            self.add_condition(i, 1, 2, self.condition)
            self.add_condition(i, 2, 3, self.condition)
            self.add_condition(i, 3, 1, self.condition)

        for i in range(2, 3):
            self.add_condition(i, 0, 1, self.condition)
            self.add_condition(i, 1, 0, self.condition)


        for i in range(4, PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

    def condition(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[0].get_current_tactic().status_flag == Flags.SUCCESS

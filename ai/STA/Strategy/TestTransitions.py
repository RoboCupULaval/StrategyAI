# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Tactic.GoalKeeper import GoalKeeper

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

        for i in range(1, PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

    def condition(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[1].get_current_tactic().status_flag == Flags.SUCCESS

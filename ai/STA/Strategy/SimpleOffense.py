# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.ProtectGoal import GoalKeeper
from . Strategy import Strategy
from ai.Algorithm.Node import Node

# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire


class SimpleOffense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.add_tactic(0, GoalKeeper(self.game_state, 0))
        for i in range(1, 6):
            self.add_tactic(i, GoGetBall(self.game_state, i))

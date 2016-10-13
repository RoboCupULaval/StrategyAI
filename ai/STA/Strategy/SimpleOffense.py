# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from . Strategy import Strategy
from ai.Algorithm.Node import Node

# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire


class SimpleOffense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.graphs[0].add_node(Node(GoalKeeper(self.game_state, 0)))
        for i in range(1, 6):
            self.graphs[i].add_node(Node(GoGetBall(self.game_state, i)))

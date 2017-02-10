# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from . Strategy import Strategy
from ai.Util.raycast import raycast2

class SimpleOffense(Strategy):
    def __init__(self, p_game_state):
        tactics =   [GoalKeeper(p_game_state, 0),
                     GoGetBall(p_game_state, 1),
                     GoGetBall(p_game_state, 2),
                     GoGetBall(p_game_state, 3),
                     GoGetBall(p_game_state, 4),
                     GoGetBall(p_game_state, 5)]
        super().__init__(p_game_state, tactics)

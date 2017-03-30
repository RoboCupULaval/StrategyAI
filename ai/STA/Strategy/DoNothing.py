# Under MIT License, see LICENSE.txt
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.Stop import Stop
from . Strategy import Strategy


class DoNothing(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for i in range(PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

# Under MIT license, see LICENSE.txt

from . Strategy import Strategy
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.Stop import Stop
from RULEngine.Util.constant import PLAYER_PER_TEAM


class HumanControl(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for i in range(PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

    def assign_tactic(self, tactic, robot_id):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)
        assert 0 <= robot_id < PLAYER_PER_TEAM

        self.graphs[robot_id].remove_node(0)
        self.add_tactic(robot_id, tactic)

# Under MIT license, see LICENSE.txt

from . Strategy import Strategy
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.Stop import Stop
from RULEngine.Util.constant import PLAYER_PER_TEAM



class HumanControl(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for player in self.game_state.my_team.available_players.values():
            self.add_tactic(player.id, Stop(self.game_state, player))

    def assign_tactic(self, tactic, robot_id):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)
        assert 0 <= robot_id < PLAYER_PER_TEAM

        self.graphs[robot_id].remove_node(0)
        self.add_tactic(robot_id, tactic)

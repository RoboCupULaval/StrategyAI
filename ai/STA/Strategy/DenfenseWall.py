# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from ai.STA.Tactic.AlignToDefenseWall import AllignToDefenseWall
from ai.STA.Tactic.Stop import Stop
from ai.states.game_state import GameState
from . Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM

class DefenseWall(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 5):
        super().__init__(game_state)
        self.number_of_players = number_of_players
        self.robots = []
        for i in range(self.number_of_players):
            self.robots += [self.game_state.my_team.available_players[i]]
        for i in range(self.number_of_players):
            self.add_tactic(self.robots[i].id, AllignToDefenseWall(self.game_state, self.robots[i], self.robots))

        for player in self.game_state.my_team.available_players.values():
            if not any(self.robots) == player:
                self.add_tactic(player.id, Stop(self.game_state, player))


    def is_ball_closest_to_player(self, player: OurPlayer):
        player_pos = player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        dist_ref = np.linalg.norm(player_pos - ball)

        for p in self.game_state.my_team.available_players.values():
            if not p == player.id:
                dist = np.linalg.norm(p.pose.position.conv_2_np() - ball)
                if dist < dist_ref:
                    return False
        return True

    def condition(self, i):
        # print(i, self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS)
        return self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS

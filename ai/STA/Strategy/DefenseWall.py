# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from ai.STA.Tactic.AlignToDefenseWall import AllignToDefenseWall
from ai.STA.Tactic.Stop import Stop
from ai.Util.role import Role
from ai.states.game_state import GameState
from . Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM

class DefenseWall(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 4, hard_code=True):
        super().__init__(game_state)
        self.number_of_players = number_of_players
        self.robots = []


        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE]
        if hard_code:
            game_state.map_players_to_roles_by_player_id({
                Role.FIRST_ATTACK: 2,
                Role.SECOND_ATTACK: 3,
                Role.MIDDLE: 4,
                Role.FIRST_DEFENCE: 5,
            })

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots]
        for role, player in role_by_robots:
            self.add_tactic(role, AllignToDefenseWall(self.game_state, player, self.robots))

        # for player in self.game_state.my_team.available_players.values():
        #     if not any(self.robots) == player:
        #         self.add_tactic(player.id, Stop(self.game_state, player))


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
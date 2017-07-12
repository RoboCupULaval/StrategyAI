# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from ai.Algorithm.evaluation_module import closest_player_to_point, closest_players_to_point
from ai.STA.Tactic.AlignToDefenseWall import AllignToDefenseWall
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.go_kick import GoKick
from ai.Util.role import Role
from ai.states.game_state import GameState
from . Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM

class DefenseWall(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        roles_to_consider = [Role.FIRST_DEFENCE, Role.SECOND_DEFENCE, Role.GOALKEEPER, Role.FIRST_ATTACK,
                             Role.SECOND_ATTACK, Role.MIDDLE]

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots[:3]]
        for role, player in role_by_robots:
            if player:
                self.add_tactic(role, AllignToDefenseWall(self.game_state, player, self.robots))
                self.add_tactic(role, GoKick(self.game_state, player))

                self.add_condition(role, 0, 1, partial(self.is_closest, player))
                self.add_condition(role, 1, 0, partial(self.is_not_closest, player))
                self.add_condition(role, 1, 1, partial(self.is_ball_closest_to_player, player))

        # for player in self.game_state.my_team.available_players.values():
        #     if not any(self.robots) == player:
        #         self.add_tactic(player.id, Stop(self.game_state, player))

    def is_closest(self, player):
        if (player == closest_players_to_point(GameState().get_ball_position(), True)[0]) or (player == closest_players_to_point(GameState().get_ball_position(), True)[1]):
            print(player.id)
            return True
        return False

    def is_not_closest(self, player):
        return player != closest_players_to_point(GameState().get_ball_position(), True)

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

    # def condition(self, i):
    #     # print(i, self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS)
    #     return self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS

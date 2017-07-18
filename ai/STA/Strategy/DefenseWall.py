# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from ai.Algorithm.evaluation_module import closest_players_to_point, Pose, Position
from ai.STA.Tactic.AlignToDefenseWall import AllignToDefenseWall
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.role import Role
from ai.states.game_state import GameState
from . Strategy import Strategy

class DefenseWall(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 4, hard_code=True):
        super().__init__(game_state)
        self.number_of_players = number_of_players
        self.robots = []
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE, Role.GOALKEEPER]
        # if hard_code:
        #     game_state.map_players_to_roles_by_player_id({
        #         Role.FIRST_ATTACK: 2,
        #         Role.SECOND_ATTACK: 3,
        #         Role.MIDDLE: 4,
        #         Role.FIRST_DEFENCE: 5,
        #         Role.SECOND_DEFENCE: 1,
        #     })

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots if player is not None]
        for role, player in role_by_robots:
            if player:
                self.add_tactic(role, AllignToDefenseWall(self.game_state, player, self.robots))
                self.add_tactic(role, GoKick(self.game_state, player, auto_update_target=True))
                self.add_tactic(role, PositionForPass(self.game_state, player, auto_position=True))

                self.add_condition(role, 0, 1, partial(self.is_closest, player))
                self.add_condition(role, 2, 1, partial(self.is_closest, player))
                self.add_condition(role, 1, 1, partial(self.is_closest, player))
                self.add_condition(role, 1, 2, partial(self.is_not_closest, player))
                self.add_condition(role, 2, 0, partial(self.is_not_one_of_the_closests, player))
                self.add_condition(role, 0, 2, partial(self.is_second_closest, player))

    def is_closest(self, player):
        if player == closest_players_to_point(GameState().get_ball_position(), True)[0].player:
            return True
        return False
    def is_second_closest(self, player):
        if player == closest_players_to_point(GameState().get_ball_position(), True)[1].player:
            return True
        return False

    def is_not_closest(self, player):
        return not(self.is_closest(player))

    def is_not_one_of_the_closests(self, player):
        print(player.id)
        print(not(self.is_closest(player) or self.is_second_closest(player)))
        return not(self.is_closest(player) or self.is_second_closest(player))

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].get_current_tactic_name() == 'GoKick':
            return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False

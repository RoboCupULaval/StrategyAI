# Under MIT License, see LICENSE.txt

from functools import partial
from math import acos

from Util.geometry import normalize
from Util.role import Role

from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.reveive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
import numpy as np


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class TestPassing(Strategy):

    def __init__(self, p_game_state, can_kick_in_goal=False):
        super().__init__(p_game_state)

        formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        initial_position_for_pass_center = {}
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            else:
                node_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                   player,
                                                                   robots_in_formation=formation,
                                                                   auto_position=True,
                                                                   forbidden_areas=[self.game_state.field.free_kick_avoid_area,
                                                                                    self.game_state.field.our_goal_forbidden_area]))
                node_wait_for_pass = self.create_node(role, ReceivePass(self.game_state, player))
                initial_position_for_pass_center[role] = node_pass.tactic.area.center  # Hack
                node_go_kick = self.create_node(role, GoKick(self.game_state,
                                                             player,
                                                             auto_update_target=True,
                                                             can_kick_in_goal=can_kick_in_goal))

                player_is_not_closest = partial(self.is_not_closest, player)
                player_has_kicked = partial(self.has_kicked, player)
                player_is_receiving_pass = partial(self.ball_going_toward_player, player)
                player_is_not_receiving_pass = partial(self.ball_not_going_toward_player, player)
                player_has_received_ball = partial(self.has_received, player)
                player_is_closest = partial(self.is_closest_not_goalkeeper, player)

                node_pass.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
                node_pass.connect_to(node_go_kick, when=player_is_closest)
                node_wait_for_pass.connect_to(node_go_kick, when=player_has_received_ball)
                node_wait_for_pass.connect_to(node_pass, when=player_is_not_receiving_pass)
                node_go_kick.connect_to(node_pass, when=player_is_not_closest)
                node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

        # Find position for ball player closest to ball
        self.closest_role = None
        ball_position = self.game_state.ball_position
        for r, position in initial_position_for_pass_center.items():
            if self.closest_role is None \
                or (initial_position_for_pass_center[self.closest_role] - ball_position).norm > \
                    (position - ball_position).norm:
                self.closest_role = r

        self.has_ball_move = False

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK,
                Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.SECOND_ATTACK,
                Role.FIRST_DEFENCE,
                Role.SECOND_DEFENCE]

    def is_closest_not_goalkeeper(self, player):
        if self.game_state.ball.is_mobile():
            self.has_ball_move = True
        role = GameState().get_role_by_player_id(player.id)
        if not self.has_ball_move:
            return role == self.closest_role

        closest_players = closest_players_to_point(GameState().ball_position, our_team=True)
        if player == closest_players[0].player:
            return True
        return closest_players[0].player == self.game_state.get_player_by_role(Role.GOALKEEPER) \
               and player == closest_players[1].player

    def is_not_closest(self, player):
        return not self.is_closest_not_goalkeeper(player)

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

    def is_ready_to_kick(self, player):
        if self.has_ball_move:
            return True  # FIXME: Test irl, might Cause a lot of problem
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'RotateAroundBall':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

    def ball_going_toward_player(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'PositionForPass' or self.roles_graph[role].current_tactic_name == 'ReceivePass':
            if self.game_state.ball.velocity.norm > 50:
                return np.dot(normalize(player.position - self.game_state.ball.position).array,
                              normalize(self.game_state.ball.velocity).array) > 0.9
        return False

    def ball_not_going_toward_player(self, player):
        return not self.ball_going_toward_player(player)

    def has_received(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'ReceivePass':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False
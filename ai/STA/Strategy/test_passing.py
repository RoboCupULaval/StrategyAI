# Under MIT License, see LICENSE.txt

from functools import partial

from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point, ball_going_toward_player, \
    ball_not_going_toward_player
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class TestPassing(Strategy):

    def __init__(self, p_game_state, can_kick_in_goal=True):
        super().__init__(p_game_state)

        formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        initial_position_for_pass_center = {}
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            else:
                node_pass = self.create_node(role,
                                             PositionForPass(self.game_state,
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
                player_is_receiving_pass = partial(ball_going_toward_player, p_game_state, player)
                player_is_not_receiving_pass = partial(ball_not_going_toward_player, p_game_state, player)
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
                Role.FIRST_DEFENCE,
                Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.SECOND_ATTACK,
                Role.FIRST_ATTACK,
                Role.SECOND_DEFENCE]

    def is_closest_not_goalkeeper(self, player):
        if self.game_state.ball.is_mobile():
            self.has_ball_move = True
        role = GameState().get_role_by_player_id(player.id)
        if not self.has_ball_move:
            return role == self.closest_role

        closest_players = closest_players_to_point(GameState().ball_position, is_our_team=True)
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

    def has_received(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'ReceivePass':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

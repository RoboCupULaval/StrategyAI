# Under MIT License, see LICENSE.txt

from functools import partial

from Util.constant import KickForce
from Util.pose import Position, Pose
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.Algorithm.evaluation_module import closest_player_to_point, closest_players_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.rotate_around_ball import RotateAroundBall
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class DirectFreeKick(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        their_goal = p_game_state.field.their_goal_pose

        formation = [p for r, p in self.assigned_roles.items() if p != Role.GOALKEEPER]
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            else:
                node_position_for_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                                player,
                                                                                robots_in_formation=formation,
                                                                                auto_position=True))
                node_rotate_around_ball = self.create_node(role, RotateAroundBall(self.game_state, player, their_goal))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, their_goal, auto_update_target=True, kick_force=KickForce.HIGH))

                player_is_closest = partial(self.is_closest_not_goalkeeper, player)
                player_is_not_closest = partial(self.is_not_closest, player)
                player_has_kicked = partial(self.has_kicked, player)
                player_is_ready_to_kick = partial(self.is_ready_to_kick, player)

                node_position_for_pass.connect_to(node_rotate_around_ball, when=player_is_closest)
                node_rotate_around_ball.connect_to(node_position_for_pass, when=player_is_not_closest)
                node_go_kick.connect_to(node_position_for_pass, when=player_is_not_closest)
                node_rotate_around_ball.connect_to(node_go_kick, when=player_is_ready_to_kick)
                node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.MIDDLE]
                }

    @classmethod
    def optional_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }

    def is_closest_not_goalkeeper(self, player):
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
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'RotateAroundBall':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

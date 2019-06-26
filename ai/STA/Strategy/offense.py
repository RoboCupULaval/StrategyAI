# Under MIT license, see LICENSE.txt
from functools import partial

from Util.role import Role

from ai.Algorithm.evaluation_module import closest_players_to_point_except, ball_going_toward_player, ball_not_going_toward_player
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_kick_3way import GoKick3Way
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class Offense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robots_in_formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        for role, player in self.assigned_roles.items():
            if role is Role.GOALKEEPER:
                self.create_node(role, GoalKeeper(self.game_state, player))
            else:
                node_position_for_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                                player,
                                                                                auto_position=True,
                                                                                robots_in_formation=robots_in_formation))
                node_go_kick = self.create_node(role, GoKick3Way(self.game_state,
                                                                       player,
                                                                       auto_update_target=True, can_kick_in_goal=False))
                node_receive_pass = self.create_node(role, ReceivePass(self.game_state, player))

                player_is_closest_and_is_not_receiving_pass = partial(self.is_closest_not_goalkeeper_and_is_not_receiving_pass, player)
                player_is_not_closest_and_is_not_making_pass = partial(self.player_is_not_closest_and_is_not_making_pass, player)
                player_has_kicked = partial(self.has_kicked, player)
                player_is_receiving_pass_or_ball_is_going_toward_player = \
                    partial(self.player_is_receiving_pass_or_ball_is_going_toward_player, p_game_state, player)
                ball_is_not_going_toward_player_and_player_is_not_receiving_pass = partial(self.ball_is_not_going_toward_player_and_player_is_not_receiving_pass, p_game_state, player)
                player_has_received_ball = partial(self.has_received, player)

                node_position_for_pass.connect_to(node_receive_pass, when=player_is_receiving_pass_or_ball_is_going_toward_player)
                node_position_for_pass.connect_to(node_go_kick, when=player_is_closest_and_is_not_receiving_pass)
                node_receive_pass.connect_to(node_go_kick, when=player_has_received_ball)
                node_receive_pass.connect_to(node_position_for_pass, when=ball_is_not_going_toward_player_and_player_is_not_receiving_pass)
                node_go_kick.connect_to(node_position_for_pass, when=player_is_not_closest_and_is_not_making_pass)
                # node_go_kick.connect_to(node_receive_pass, when=player_is_receiving_pass)
                node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK,
                Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_DEFENCE,
                Role.SECOND_ATTACK,
                Role.SECOND_DEFENCE]

    def is_closest_not_goalkeeper(self, player):
        ban_players = self.game_state.ban_players
        if player in ban_players:
            return False

        closests = closest_players_to_point_except(self.game_state.ball.position,
                                                   except_roles=[Role.GOALKEEPER],
                                                   except_players=ban_players)

        return len(closests) > 0 and closests[0].player == player

    def ball_is_not_going_toward_player_and_player_is_not_receiving_pass(self, game_state, player):
        return ball_not_going_toward_player(game_state, player) and not self.is_receiving_pass(player)

    def is_closest_not_goalkeeper_and_is_not_receiving_pass(self, player):
        return self.is_closest_not_goalkeeper(player) and not self.is_receiving_pass(player)

    def player_is_not_closest_and_is_not_making_pass(self, player):
        return not self.is_closest_not_goalkeeper(player) and not self.is_making_a_pass(player)

    def is_making_a_pass(self, player):
        role = self.game_state.get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            if self.roles_graph[role].current_tactic.status_flag == Flags.PASS_TO_PLAYER:
                return True
        return False

    def has_kicked(self, player):
        role = self.game_state.get_role_by_player_id(player.id)
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

    def player_is_receiving_pass_or_ball_is_going_toward_player(self, game_state, player):
        return self.is_receiving_pass(player)  # or ball_going_toward_player(game_state, player)

    # TODO assigner passing_robot_pose ou passing_robot à la tactic du receptionneur de passe
    def is_receiving_pass(self, player):
        for role, p in self.assigned_roles.items():
            if self.roles_graph[role].current_tactic_name == 'GoKick':
                if self.roles_graph[role].current_tactic.status_flag == Flags.PASS_TO_PLAYER:
                    is_receiving = player == self.roles_graph[role].current_tactic.current_player_target
                    if is_receiving:
                        self.logger.info(f"=============== *** robot {p} is passing to robot {player}")
                    return is_receiving
        return False

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
                node_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                   player,
                                                                   auto_position=True,
                                                                   robots_in_formation=robots_in_formation))
                node_go_kick = self.create_node(role, GoKick3Way(self.game_state,
                                                                 player,
                                                                 auto_update_target=True))
                node_wait_for_pass = self.create_node(role, ReceivePass(self.game_state, player))

                player_is_closest = partial(self.is_closest_not_goalkeeper, player)
                player_is_not_closest = partial(self.is_not_closest, player)
                player_has_kicked = partial(self.has_kicked, player)
                player_is_receiving_pass = partial(ball_going_toward_player, p_game_state, player)
                player_is_not_receiving_pass = partial(ball_not_going_toward_player, p_game_state, player)
                player_has_received_ball = partial(self.has_received, player)

                node_pass.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
                node_pass.connect_to(node_go_kick, when=player_is_closest)
                node_wait_for_pass.connect_to(node_go_kick, when=player_has_received_ball)
                node_wait_for_pass.connect_to(node_pass, when=player_is_not_receiving_pass)
                node_go_kick.connect_to(node_pass, when=player_is_not_closest)
                # node_go_kick.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
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

    def is_not_closest(self, player):
        return not self.is_closest_not_goalkeeper(player)

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
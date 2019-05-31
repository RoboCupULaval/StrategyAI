# Under MIT license, see LICENSE.txt

from Util.role import Role

from ai.Algorithm.evaluation_module import closest_players_to_point_except, ball_going_toward_player
from ai.STA.Strategy.graphless_strategy import GraphlessStrategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class GraphlessOffense(GraphlessStrategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.robots_in_formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        for role, player in self.assigned_roles.items():
            if role is Role.GOALKEEPER:
                self.roles_to_tactics[role] = GoalKeeper(self.game_state, player)
            else:
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              auto_position=True,
                                                              robots_in_formation=self.robots_in_formation)
        self.next_state = self.go_get_ball

        self.current_pass_receiver = None

    def go_get_ball(self):
        for role, player in self.assigned_roles.items():
            tactic = self.roles_to_tactics[role]
            if isinstance(tactic, GoKick):
                if not self.is_closest_not_goalkeeper(player):
                    self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                                  player,
                                                                  auto_position=True,
                                                                  robots_in_formation=self.robots_in_formation)
                elif tactic.status_flag == Flags.PASS_TO_PLAYER:
                    self.current_pass_receiver = tactic.current_player_target
                    self.next_state = self.receive_pass
                    return  # We dont want to override self.current_pass_receiver

            elif isinstance(tactic, PositionForPass) and self.is_closest_not_goalkeeper(player):
                self.roles_to_tactics[role] = GoKick(self.game_state,
                                                     player,
                                                     auto_update_target=True,
                                                     can_kick_in_goal=False)

            elif ball_going_toward_player(self.game_state, player):
                self.current_pass_receiver = player
                self.next_state = self.receive_pass

    def receive_pass(self):
        last_receiver_role = self.game_state.get_role_by_player_id(self.current_pass_receiver.id)
        last_receiver_tactic = self.roles_to_tactics[last_receiver_role]

        for role, player in self.assigned_roles.items():
            tactic = self.roles_to_tactics[role]
            if isinstance(tactic, GoKick):
                gokick_target = tactic.current_player_target

                if gokick_target is not None:
                    if gokick_target != self.current_pass_receiver:
                        new_receiver_role = self.game_state.get_role_by_player_id(gokick_target.id)

                        last_receiver_tactic = PositionForPass(self.game_state,
                                                               player,
                                                               auto_position=True,
                                                               robots_in_formation=self.robots_in_formation)

                        self.roles_to_tactics[new_receiver_role] = ReceivePass(self.game_state, player)

                        self.current_pass_receiver = gokick_target
                elif not isinstance(last_receiver_tactic, ReceivePass):  # It was not a real pass
                    last_receiver_tactic = ReceivePass(self.game_state, player)

            elif isinstance(tactic, ReceivePass) and self.has_received(player):
                self.next_state = self.go_get_ball

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

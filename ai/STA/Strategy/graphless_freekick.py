# Under MIT License, see LICENSE.txt

from Util.constant import IN_PLAY_MIN_DISTANCE
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point_except, \
    ball_going_toward_player
from ai.GameDomainObjects import Player
from ai.STA.Strategy.graphless_strategy import GraphlessStrategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class GraphlessFreeKick(GraphlessStrategy):

    def __init__(self, p_game_state, can_kick_in_goal):
        super().__init__(p_game_state)

        self.robots_in_formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        self.forbidden_areas = [self.game_state.field.free_kick_avoid_area,
                           self.game_state.field.our_goal_forbidden_area]

        initial_position_for_pass_center = {}
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.roles_to_tactics[role] = GoalKeeper(self.game_state, player)
            else:
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              robots_in_formation=self.robots_in_formation,
                                                              auto_position=True,
                                                              forbidden_areas=self.game_state.field.border_limits
                                                                              + self.forbidden_areas)

                initial_position_for_pass_center[role] = self.roles_to_tactics[role].area.center  # Hack

        # Find position for ball player closest to ball
        self.closest_role = None
        ball_position = self.game_state.ball_position
        for r, position in initial_position_for_pass_center.items():
            if self.closest_role is None \
                or (initial_position_for_pass_center[self.closest_role] -
                    ball_position).norm > (position - ball_position).norm:
                self.closest_role = r

        self.ball_start_position = self.game_state.ball.position
        self.next_state = self.go_get_ball
        self.current_pass_receiver = None
        self.can_kick_in_goal = can_kick_in_goal

    def go_get_ball(self):
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                continue
            tactic = self.roles_to_tactics[role]
            if isinstance(tactic, GoKick):
                if not self.is_closest_not_goalkeeper(player):
                    self.logger.info(f"Robot {player.id} was not closest. Returning to PositionForPass")
                    self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                                  player,
                                                                  auto_position=True,
                                                                  robots_in_formation=self.robots_in_formation)
                elif tactic.status_flag == Flags.PASS_TO_PLAYER and self._is_close_to_ball(player):
                    self.logger.info(
                        f"Robot {player.id} decided to make a pass to Robot {tactic.current_player_target.id}")
                    self._assign_target_to_receive_pass(tactic.current_player_target, passing_robot=player)

                    self.logger.info("Switching to receive_pass")
                    self.next_state = self.receive_pass
                    return  # We dont want to override self.current_pass_receiver

            elif self.is_closest_not_goalkeeper(player):
                self.logger.info(f"Robot {player.id} is closest! Switching to GoKick")
                self.roles_to_tactics[role] = GoKick(self.game_state,
                                                     player,
                                                     auto_update_target=True,
                                                     can_kick_in_goal=self.can_kick_in_goal,
                                                     forbidden_areas=self.game_state.field.border_limits
                                                                     + self.forbidden_areas
                                                     )

            elif ball_going_toward_player(self.game_state, player):
                self.logger.info(f"Ball is going toward Robot {player.id}!")
                self._assign_target_to_receive_pass(player, passing_robot=None)

                self.logger.info("Switching to receive_pass")
                self.next_state = self.receive_pass

    def receive_pass(self):
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                continue
            tactic = self.roles_to_tactics[role]
            if isinstance(tactic, GoKick):
                gokick_target = tactic.current_player_target
                if gokick_target is not None:
                    if gokick_target != self.current_pass_receiver:
                        self.logger.info(
                            f"Robot {player.id} changed its target! Last target: Robot {self.current_pass_receiver.id}  -- New target : {gokick_target.id}")

                        self.logger.info(f"Switching Robot {self.current_pass_receiver.id} tactic to PositionForPass")
                        last_receiver_role = self.game_state.get_role_by_player_id(self.current_pass_receiver.id)

                        self.roles_to_tactics[last_receiver_role] = PositionForPass(self.game_state,
                                                                                    self.current_pass_receiver,
                                                                                    auto_position=True,
                                                                                    robots_in_formation=self.robots_in_formation)

                        self._assign_target_to_receive_pass(gokick_target, player)

                    if tactic.status_flag == Flags.SUCCESS:
                        self.logger.info(f"Robot {player.id} has kicked!")
                        receiver_role = self.game_state.get_role_by_player_id(self.current_pass_receiver.id)
                        receiver_tactic = self.roles_to_tactics[receiver_role]
                        assert isinstance(receiver_tactic, ReceivePass)
                        receiver_tactic.passing_robot_has_kicked = True

            elif isinstance(tactic, ReceivePass) and tactic.status_flag == Flags.SUCCESS:
                self.logger.info(f"Robot {player.id} has received ball!")
                self.logger.info("Switching to go_get_ball")
                self.next_state = self.go_get_ball

    def _assign_target_to_receive_pass(self, target: Player, passing_robot):
        self.logger.info(f"Switching Robot {target.id} tactic to ReceivePass")
        role = self.game_state.get_role_by_player_id(target.id)
        self.roles_to_tactics[role] = ReceivePass(self.game_state, target, passing_robot=passing_robot)
        self.current_pass_receiver = target

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
        ban_players = self.game_state.double_touch_checker.ban_players
        if player in ban_players:
            return False

        role = self.game_state.get_role_by_player_id(player.id)
        if (self.ball_start_position - self.game_state.ball.position).norm <= IN_PLAY_MIN_DISTANCE:
            return role == self.closest_role

        closests = closest_players_to_point_except(self.game_state.ball.position,
                                                   except_roles=[Role.GOALKEEPER],
                                                   except_players=ban_players)
        return len(closests) > 0 and closests[0].player == player

    def _is_close_to_ball(self, player: Player):
        return (self.game_state.ball_position - player.position).norm < MAX_DISTANCE_TO_SWITCH_TO_RECEIVE_PASS
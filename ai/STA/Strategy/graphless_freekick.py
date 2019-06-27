# Under MIT License, see LICENSE.txt
import time

import math

from Util import Pose
from Util.constant import IN_PLAY_MIN_DISTANCE, ROBOT_RADIUS
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point_except, \
    ball_going_toward_player
from ai.GameDomainObjects import Player
from ai.STA.Strategy.graphless_strategy import GraphlessStrategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags

TIME_TO_GET_IN_POSITION = 5


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
        self.next_state = self.get_in_position
        self.current_pass_receiver = None
        self.can_kick_in_goal = can_kick_in_goal
        self.first_passing_player = None

        self.start_time = time.time()

    def get_in_position(self):
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                continue
            if self.is_closest_not_goalkeeper(player):
                self.logger.info(f"Robot {player.id} is closest => go behind ball")
                self.first_passing_player = player

                their_goal_to_ball = self.game_state.ball_position - self.game_state.field.their_goal
                go_behind_position = self.game_state.ball_position + their_goal_to_ball.unit * ROBOT_RADIUS * 2.0
                go_behind_orientation = their_goal_to_ball.angle + math.pi
                self.roles_to_tactics[role] = GoToPosition(self.game_state,
                                                           player,
                                                           target=Pose(go_behind_position, go_behind_orientation),
                                                           cruise_speed=1)
            else:
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              auto_position=True,
                                                              robots_in_formation=self.robots_in_formation)

        self.next_state = self.wait_before_pass

    def wait_before_pass(self):
        if time.time() - self.start_time > TIME_TO_GET_IN_POSITION:
            self.next_state = self.pass_to_receiver

    def pass_to_receiver(self):
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
                elif tactic.status_flag == Flags.PASS_TO_PLAYER:
                    self.logger.info(
                        f"Robot {player.id} decided to make a pass to Robot {tactic.current_player_target.id}")
                    self._assign_target_to_receive_pass(tactic.current_player_target, passing_robot=player)

                    self.logger.info("Switching to receive_pass")
                    self.next_state = self.receive_pass
                    return  # We dont want to override self.current_pass_receiver

            elif self.is_closest_not_goalkeeper(player):
                self.logger.info(f"Robot {player.id} is closest! Switching to GoKick")

                can_kick_in_goal = self.can_kick_in_goal if self.first_passing_player else True
                self.roles_to_tactics[role] = GoKick(self.game_state,
                                                     player,
                                                     auto_update_target=True,
                                                     can_kick_in_goal=can_kick_in_goal,
                                                     forbidden_areas=self.game_state.field.border_limits
                                                                     + self.forbidden_areas
                                                     )

            elif ball_going_toward_player(self.game_state, player):
                self.logger.info(f"Ball is going toward Robot {player.id}!")
                self._assign_target_to_receive_pass(player, passing_robot=None)

                self.logger.info("Switching to receive_pass")
                self.next_state = self.receive_pass

            # Robots must not stay in receive pass if they are not receiving a pass
            elif isinstance(tactic, ReceivePass):
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              auto_position=True,
                                                              robots_in_formation=self.robots_in_formation)

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
                self.next_state = self.pass_to_receiver

        # FIXME
        if all(not isinstance(self.roles_to_tactics[role], GoKick) for role, _ in self.assigned_roles.items()):
            self.logger.info("No robot is assigned to GoKick! Switching to go_get_ball")
            self.next_state = self.pass_to_receiver

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


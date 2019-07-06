# Under MIT licence, see LICENCE.txt

import math as m
import time
from typing import List, Union

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory, MAGENTA, CYAN
from Util.constant import ROBOT_CENTER_TO_KICKER, BALL_RADIUS, KickForce, ROBOT_RADIUS
from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle, MoveTo
from Util.geometry import compare_angle, normalize, angle_between_three_points
from ai.Algorithm.evaluation_module import best_passing_option, player_covered_from_goal, closest_players_to_point
from ai.GameDomainObjects import Player
from ai.STA.Tactic.go_kick import MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_TO_PASS, \
    MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_FROM_PASS
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from ai.Algorithm.evaluation_module import object_going_toward_other_object, ball_going_toward_player
from Util.geometry import normalize, Line, closest_point_on_segment
from config.config import Config

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1.0

GO_BEHIND_SPACING = 250
GRAB_BALL_SPACING = 120
APPROACH_SPEED = 100
KICK_DISTANCE = 120
KICK_SUCCEED_THRESHOLD = 300
COMMAND_DELAY = 0.5


class GoKick3Way(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose = Pose(),
                 args: List[str] = None,
                 kick_force: KickForce = KickForce.HIGH,
                 auto_update_target=True,
                 go_behind_distance=GRAB_BALL_SPACING * 3,
                 forbidden_areas=None,
                 can_kick_in_goal=True):

        super().__init__(game_state, player, target, args=args, forbidden_areas=forbidden_areas)
        self.current_state = self.initialize
        self.next_state = self.go_behind_ball
        self.kick_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.can_kick_in_goal = can_kick_in_goal
        self.target_assignation_last_time = 0
        self.target = target

        self.current_player_target = None
        self.nb_consecutive_times_a_pass_is_decided = 0
        self.nb_consecutive_times_a_pass_is_not_decided = 0

        if self.auto_update_target:
            self._find_best_passing_option()

        self.kick_force = kick_force
        self.go_behind_distance = go_behind_distance

        self.when_kicking_target = None
        self.when_kicking_ball = None
        self.when_targeting_target = None
        self.when_targeting_ball = None
        self.when_targeting_goalkeeper = None

        self.enable_log_state = False

    def initialize(self):
        if self.auto_update_target:
            self._find_best_passing_option()
        self.check_ball_state()

        return Idle

    def check_ball_state(self):
        if self.game_state.ball.velocity.norm > 200:
            if self.is_ball_going_toward_target():
                if self.is_ball_going_toward_player() and self._get_distance_from_ball() > 500:
                    self.next_state = self.intercept
                else:
                    self.next_state = self.chase_ball
            elif self.is_ball_going_toward_player(110) and self._get_distance_from_ball() > 500:
                self.next_state = self.intercept
            else:
                self.next_state = self.go_behind_ball
        elif self.is_able_to_grab_ball_directly(m.cos(np.deg2rad(10))) and self._get_distance_from_ball() < KICK_DISTANCE:
            self.next_state = self.kick
        else:
            self.next_state = self.go_behind_ball

    def go_behind_ball(self):
        if self.enable_log_state:
            self.logger.info("Go behind")
        if self.auto_update_target:
            self._find_best_passing_option()
        self.status_flag = Flags.WIP
        orientation = (self.target.position - self.game_state.ball_position).angle
        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_modifier = (ball_speed / 1000 + 1)
        angle_behind = self.get_alligment_with_ball_and_target()
        if angle_behind > 40:
            effective_ball_spacing = GRAB_BALL_SPACING * min(2, abs(angle_behind / 40)) * ball_speed_modifier
            collision_ball = True
        else:
            effective_ball_spacing = GRAB_BALL_SPACING
            collision_ball = False
        vec_ball_to_player = normalize(self.game_state.ball_position - self.player.position)
        perpendicular_ball_velocity = self.game_state.ball.velocity - vec_ball_to_player * np.dot(
            self.game_state.ball.velocity.array, vec_ball_to_player.array)
        distance_behind = self.get_destination_behind_ball(effective_ball_spacing,
                                                           ball_velocity_vector=perpendicular_ball_velocity)
        if self.is_able_to_grab_ball_directly(0.95) \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.next_state = self.grab_ball
        else:
            self.check_ball_state()
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=collision_ball) \
            .addChargeKicker().build()

    def chase_ball(self):
        if self.enable_log_state:
            self.logger.info("Chase")
        if self.auto_update_target:
            self._find_best_passing_option()
        self.status_flag = Flags.WIP
        orientation = (self.target.position - self.game_state.ball_position).angle
        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_modifier = (ball_speed / 1000 + 1)
        angle_behind = self.get_alligment_with_ball_and_target()
        if angle_behind > 20:
            effective_ball_spacing = GRAB_BALL_SPACING * min(2, abs(angle_behind / 40)) * ball_speed_modifier
            collision_ball = True
        else:
            effective_ball_spacing = GRAB_BALL_SPACING
            collision_ball = False
        vec_ball_to_player = normalize(self.game_state.ball_position - self.player.position)
        perpendicular_ball_velocity = self.game_state.ball.velocity - vec_ball_to_player * np.dot(
            self.game_state.ball.velocity.array, vec_ball_to_player.array)
        distance_behind = self.get_destination_behind_ball(effective_ball_spacing,
                                                           ball_velocity_vector=perpendicular_ball_velocity)
        end_speed = ball_speed
        if self.is_able_to_grab_ball_directly(0.95) \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.next_state = self.grab_ball
        else:
            self.check_ball_state()
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=end_speed,
                                      ball_collision=collision_ball) \
            .addChargeKicker().build()

    def stop_ball(self):
        if self.enable_log_state:
            self.logger.info("Stop ball")
        if self.auto_update_target:
            self._find_best_passing_option()
        self.status_flag = Flags.WIP
        orientation = (self.target.position - self.game_state.ball_position).angle
        ball_speed = self.game_state.ball.velocity.norm
        position_behind = self.get_destination_to_stop_ball(GRAB_BALL_SPACING*2)
        end_speed = ball_speed + 500
        if self.is_able_to_stop_ball(0.95) \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.next_state = self.grab_ball
        else:
            self.check_ball_state()
        return CmdBuilder().addMoveTo(Pose(position_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=end_speed,
                                      ball_collision=True) \
            .addChargeKicker().build()

    def wait_for_ball(self):
        if self.enable_log_state:
            self.logger.info("wait for ball")
        self.check_ball_state()
        orientation = (self.target.position - self.game_state.ball_position).angle
        position_behind = self.get_destination_to_stop_ball(0)

        return CmdBuilder().addMoveTo(Pose(position_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=False) \
            .addChargeKicker().build()

    def grab_ball(self):
        if self.enable_log_state:
           self.logger.info("Grab ball")
        if self.auto_update_target:
            self._find_best_passing_option()
        if not self.is_able_to_grab_ball_directly(0.85):
            self.next_state = self.go_behind_ball

        if self._get_distance_from_ball() < KICK_DISTANCE and self.is_able_to_grab_ball_directly(0.65):
            self.next_state = self.kick
            self.kick_last_time = time.time()
        ball_speed = self.game_state.ball.velocity.norm
        vec_ball_to_player = normalize(self.game_state.ball_position - self.player.position)
        perpendicular_ball_velocity = self.game_state.ball.velocity - vec_ball_to_player * np.dot(
            self.game_state.ball.velocity.array, vec_ball_to_player.array)
        end_speed = ball_speed
        orientation = (self.target.position - self.game_state.ball_position).angle
        distance_behind = self.get_destination_behind_ball(0, ball_velocity_vector=perpendicular_ball_velocity)
        if self._get_distance_from_ball() > KICK_DISTANCE*1.5:
            return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                          cruise_speed=3,
                                          end_speed=end_speed,
                                          ball_collision=False) \
                .addForceDribbler() \
                .addChargeKicker().addKick(kick_force=self.kick_force) \
                .build()

        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=end_speed,
                                      ball_collision=False) \
            .addForceDribbler() \
            .addChargeKicker() \
            .build()

    def kick(self):
        if self.enable_log_state:
           self.logger.info("Kick")
        self.when_kicking_target = self.target.position
        self.when_kicking_ball = self.game_state.ball_position
        if self.auto_update_target:
            self._find_best_passing_option()
        if not self.is_able_to_grab_ball_directly(0.7):
            self.next_state=self.grab_ball
            return self.next_state()
        self.check_ball_state()
        ball_speed = self.game_state.ball.velocity.norm
        end_speed = ball_speed
        behind_ball = self.game_state.ball_position
        orientation = (self.target.position - self.game_state.ball_position).angle
        if self.player.id not in Config()["COACH"]["working_kicker_ids"]:
            player_to_ball = normalize(self.game_state.ball_position - self.player.pose.position)
            ram_position = Pose(player_to_ball*100+self.game_state.ball_position, orientation)
            return CmdBuilder().addMoveTo(ram_position,
                                          ball_collision=False,
                                          cruise_speed=3,
                                          end_speed=2).build()
        else:

            return CmdBuilder().addMoveTo(Pose(behind_ball, orientation),
                              ball_collision=False,
                              cruise_speed=3,
                              end_speed=end_speed) \
                .addKick(self.kick_force) \
                .addForceDribbler().build()

    def validate_kick(self):
        if self.game_state.ball.is_moving_fast() and self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.kick
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.kick
        else:
            self.status_flag = Flags.INIT
            self.next_state = self.go_behind_ball

        return CmdBuilder().addForceDribbler().build()

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.initialize
        else:
            self.status_flag = Flags.SUCCESS
        return Idle

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi / 30):
        ball_position = self.game_state.ball_position
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle, ball_to_player.angle, abs_tol=abs_tol)

    def _find_best_passing_option(self):
        # Update passing target
        if self.current_player_target is not None:
            self.target = Pose(self.current_player_target.position)
            self.kick_force = KickForce.for_dist((self.target.position - self.game_state.ball.position).norm)

        # Update decision
        assignation_delay = (time.time() - self.target_assignation_last_time)
        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            scoring_target = player_covered_from_goal(self.player)
            tentative_target = best_passing_option(self.player, passer_can_kick_in_goal=self.can_kick_in_goal)

            # Kick in the goal where it's the easiest
            if self.can_kick_in_goal and scoring_target is not None:
                self.nb_consecutive_times_a_pass_is_decided = 0
                self.nb_consecutive_times_a_pass_is_not_decided += 1
                if not self.status_flag == Flags.PASS_TO_PLAYER or self.nb_consecutive_times_a_pass_is_not_decided >= MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_FROM_PASS:
                    self.current_player_target = None
                    self.status_flag = Flags.WIP

                    self.target = Pose(scoring_target, 0)
                    self.kick_force = KickForce.HIGH
                    self.when_targeting_ball = self.game_state.ball_position
                    self.when_targeting_target = self.target.position

                    closest_enemy = closest_players_to_point(self.game_state.field.their_goal, our_team=False)
                    if len(closest_enemy) == 0:
                        self.when_targeting_goalkeeper = None
                    else:
                        goalkeeper = closest_enemy[0].player
                        self.when_targeting_goalkeeper = goalkeeper.position

            # Kick in the goal center
            elif tentative_target is None:
                self.nb_consecutive_times_a_pass_is_decided = 0
                self.nb_consecutive_times_a_pass_is_not_decided += 1
                if not self.status_flag == Flags.PASS_TO_PLAYER or self.nb_consecutive_times_a_pass_is_not_decided >= MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_FROM_PASS:
                    self.current_player_target = None
                    self.status_flag = Flags.WIP

                    if not self.can_kick_in_goal:
                        self.logger.warning(
                            "The kicker {} can not find an ally to pass to and can_kick_in_goal is False"
                            ". So it kicks directly in the goal, sorry".format(self.player))
                    self.target = Pose(self.game_state.field.their_goal, 0)
                    self.kick_force = KickForce.HIGH

            # Pass the ball to another player
            else:
                self.nb_consecutive_times_a_pass_is_decided += 1
                self.nb_consecutive_times_a_pass_is_not_decided = 0
                if self.status_flag == Flags.INIT or \
                        (
                                not self.status_flag == Flags.PASS_TO_PLAYER and self.nb_consecutive_times_a_pass_is_decided >= MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_TO_PASS):
                    self.current_player_target = tentative_target
                    self.status_flag = Flags.PASS_TO_PLAYER

                    self.target = Pose(tentative_target.position)
                    self.kick_force = KickForce.for_dist((self.target.position - self.game_state.ball.position).norm)

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing, velocity=True, velocity_offset=15,
                                    ball_velocity_vector=Position()) -> Position:
        """
         Compute the point which is at ball_spacing mm behind the ball from the target.
        """

        dir_ball_to_target = normalize(self.target.position - self.game_state.ball.position)

        position_behind = self.game_state.ball.position - dir_ball_to_target * ball_spacing

        if velocity and self.game_state.ball.velocity.norm > 20:
            position_behind += (self.game_state.ball.velocity - (normalize(self.game_state.ball.velocity) *
                                                                 np.dot(dir_ball_to_target.array,
                                                                        self.game_state.ball.velocity.array))) / velocity_offset

        return position_behind + ball_velocity_vector / 10

    def get_destination_to_stop_ball(self, ball_spacing) -> Position:
        """
         Compute the point which is at ball_spacing mm behind the ball from the target.
        """

        dir_ball_speed = normalize(self.game_state.ball.velocity)

        position_behind = self.game_state.ball.position - dir_ball_speed * ball_spacing

        return position_behind

    def is_able_to_grab_ball_directly(self, threshold):
        # plus que le threshold est gors (1 max), plus qu'on veut que le robot soit direct deriere la balle.
        vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        alignement_behind = np.dot(vec_target_to_ball.array,
                                   (normalize(self.player.position - self.game_state.ball_position)).array)
        return threshold < alignement_behind

    def is_able_to_stop_ball(self, threshold):
        # plus que le threshold est gors (1 max), plus qu'on veut que le robot soit direct deriere la balle.
        vec_robot_to_ball = normalize(self.game_state.ball.position - self.player.position)
        alignement_behind = np.dot(vec_robot_to_ball.array,
                                   (normalize(self.game_state.ball_velocity).array))
        return threshold < alignement_behind

    def get_alligment_with_ball_and_target(self):

        vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        alignement_behind = np.dot(vec_target_to_ball.array,
                                   (normalize(self.player.position - self.game_state.ball_position)).array)
        return np.arccos(alignement_behind) * 180 / np.pi

    def is_ball_going_toward_target(self):
        return object_going_toward_other_object(self.game_state.ball, self.target, max_angle_of_approach=40)

    def is_ball_going_toward_player(self, angle=40):
        return ball_going_toward_player(self.game_state, self.player, max_angle_of_approach=angle)

    def is_ball_going_away_from_player(self, angle=90):
        return ball_going_toward_player(self.game_state, self.player, max_angle_of_approach=angle)

    def intercept(self):
        ball = self.game_state.ball

        self.check_ball_state()
        ball_trajectory = Line(ball.position, ball.position + ball.velocity)
        target_pose = self._find_target_pose(ball, ball_trajectory)
        if self._get_distance_from_ball() < KICK_DISTANCE * 1.5:
            return CmdBuilder().addMoveTo(target_pose,
                                   ball_collision=False,
                                   cruise_speed=3) \
                .addKick(self.kick_force) \
                .addForceDribbler().build()
        else:
            return CmdBuilder().addMoveTo(target_pose,
                                          ball_collision=False,
                                          cruise_speed=3,
                                          end_speed=2) \
                .addForceDribbler().build()

    def _find_target_pose(self, ball, ball_trajectory):
        # Find the point where the ball will leave the field
        where_ball_leaves_field = self._find_where_ball_leaves_field(ball, ball_trajectory)

        ball_to_leave_field = Line(ball.position, where_ball_leaves_field)

        # The robot can intercepts the ball by leaving the field, thus we must add a ROBOT_RADIUS
        intersect_position_limit = where_ball_leaves_field + ball_to_leave_field.direction * ROBOT_RADIUS
        intersect_position = closest_point_on_segment(self.player.position, ball.position, intersect_position_limit)

        if (self.player.position - intersect_position).norm < ROBOT_RADIUS:
            best_orientation = (ball.position - intersect_position_limit).angle
        else:
            best_orientation = self.player.pose.orientation  # We move a bit faster, if we keep our orientation
        orientation = (self.target.position - self.game_state.ball_position).angle
        return Pose(intersect_position, orientation)

    def _find_where_ball_leaves_field(self, ball, trajectory):
        intersection_with_field = self.game_state.field.area.intersect_with_line(trajectory)
        where_ball_leaves_field = None
        for inter in intersection_with_field:
            # If this is the intersection that have the same direction as trajectory direction
            if (inter - ball.position).dot(trajectory.direction) > 0:
                where_ball_leaves_field = inter
                break

        if where_ball_leaves_field is None:
            self.logger.error(f"_find_where_ball_leaves_field - ball: {ball.position}, trajectory: {trajectory}")
            self.logger.error(f"_find_where_ball_leaves_field - intersections_with_field: {intersection_with_field}")
            return Position()

        return where_ball_leaves_field


    def debug_cmd(self):

        if self.when_kicking_target is None or self.when_targeting_ball is None:
            return []
        cmd = [DebugCommandFactory.line(self.when_targeting_target, self.when_targeting_ball, color=CYAN, timeout=10),
               DebugCommandFactory.line(self.when_kicking_target, self.when_kicking_ball, timeout=10)]
        if self.when_targeting_goalkeeper is not None:
            cmd.append(DebugCommandFactory.circle(self.when_targeting_goalkeeper, ROBOT_RADIUS, timeout=10))
        return cmd
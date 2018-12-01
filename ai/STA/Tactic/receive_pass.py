# Under MIT licence, see LICENCE.txt

import numpy as np
from typing import Optional

from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle, MoveTo
from Util.constant import ROBOT_RADIUS
from Util.geometry import compare_angle, normalize, perpendicular, closest_point_on_line, Line, closest_point_on_segment

from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags

from ai.GameDomainObjects import Player
from ai.states.game_state import GameState

GO_BEHIND_SPACING = 250
GRAB_BALL_SPACING = 100
HAS_BALL_DISTANCE = 130
KICK_SUCCEED_THRESHOLD = 300


class ReceivePass(Tactic):

    def __init__(self, game_state: GameState, player: Player, target: Optional[Pose]=None):
      
        super().__init__(game_state, player, target)
        self.current_state = self.initialize
        self.next_state = self.initialize

    def initialize(self):
        self.status_flag = Flags.WIP
        self.next_state = self.intercept

        return Idle

    def intercept(self):
        ball = self.game_state.ball
        if self.game_state.field.is_outside_wall_limit(ball.position):
            self.logger.info("The ball has leave field")
            self.next_state = self.halt
            return Idle

        if self.game_state.ball.is_immobile():
            self.logger.info("The ball is not moving, succes?")
            self.next_state = self.halt
            return Idle

        if (ball.position - self.player.position).norm < ROBOT_RADIUS + 50:
            self.logger.info("The ball about to touch us, succes?")
            self.next_state = self.halt
            return Idle

        # Find the point where the ball will go
        ball_trajectory = Line(ball.position, ball.position + ball.velocity)
        intersection_with_field = self.game_state.field.area.intersect_with_line(ball_trajectory)

        where_ball_enter_leave_field = None
        for inter in intersection_with_field:
            # If this is the intersection that have the same direction as ball.velocity
            if (inter - ball.position).dot(ball.velocity) > 0:
                where_ball_enter_leave_field = inter
                break

        if where_ball_enter_leave_field is None:
            raise RuntimeError("How did I get here?")

        # The robot can intercepts the ball by leaving the field, thus we must add a ROBOT_RADIUS
        ball_to_leave_field = Line(ball.position, where_ball_enter_leave_field)
        end_segment = where_ball_enter_leave_field + ball_to_leave_field.direction * ROBOT_RADIUS

        intersect_pts = closest_point_on_segment(self.player.position,
                                                 ball.position, end_segment)
        return MoveTo(Pose(intersect_pts, self.player.pose.orientation),  # It's a bit faster, to keep our orientation
                      cruise_speed=3,
                      end_speed=0,
                      ball_collision=False)

    def go_behind_ball(self):
        orientation = (self.game_state.ball_position - self.player.position).angle
        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_modifier = (ball_speed/1000 + 1)
        effective_ball_spacing = GRAB_BALL_SPACING * 3 * ball_speed_modifier
        distance_behind = self.get_destination_behind_ball(effective_ball_spacing)
        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        if self.is_ball_going_to_collide(threshold=18) \
                and compare_angle(self.player.pose.orientation, orientation,
                                  abs_tol=max(0.1, 0.1 * dist_from_ball/100)):
            self.next_state = self.wait_for_ball
        else:
            self.next_state = self.go_behind_ball
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=True)\
                           .addChargeKicker().build()

    def grab_ball(self):
        if not self.is_ball_going_to_collide(threshold=18):
            self.next_state = self.go_behind_ball

        if self._get_distance_from_ball() < HAS_BALL_DISTANCE:
            self.next_state = self.halt
            return self.halt()
        orientation = (self.game_state.ball_position - self.player.position).angle
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=False).addChargeKicker().build()

    # def wait_for_ball(self):
    #     print("waiting for ball")
    #     ball_pos = self.game_state.ball.position
    #     ball_vel = self.game_state.ball.velocity
    #     col = closest_point_on_line(self.player.position, ball_pos, ball_pos + ball_vel)
    #     if self._get_distance_from_ball() < HAS_BALL_DISTANCE:
    #         print("Distance from ball is ok for pass", self._get_distance_from_ball())
    #         self.next_state = self.halt
    #         return self.halt()
    #     if not self.is_ball_going_to_collide(threshold=18):
    #         self.next_state = self.wait_for_ball
    #         return CmdBuilder().build()
    #     orientation = (self.game_state.ball_position - self.player.position).angle
    #     return CmdBuilder().addMoveTo(Pose(col, orientation),
    #                                   cruise_speed=3,
    #                                   end_speed=0,
    #                                   ball_collision=False).addChargeKicker().build()

    def wait_for_ball(self):
        # print("waiting for ball")
        perp_vec = perpendicular(self.player.position - self.game_state.ball.position)
        component_lateral = perp_vec * np.dot(perp_vec.array, normalize(self.game_state.ball.velocity).array)
        small_segment_len = np.sqrt(1 - component_lateral.norm**2)
        latteral_move = component_lateral / small_segment_len * (self.player.position - self.game_state.ball.position).norm
        if self._get_distance_from_ball() < HAS_BALL_DISTANCE:
            # print("Distance from ball is ok for pass", self._get_distance_from_ball())
            self.next_state = self.halt
            return self.halt()
        if not self.is_ball_going_to_collide(threshold=18):
            self.next_state = self.wait_for_ball
            return CmdBuilder().build()
        orientation = (self.game_state.ball_position - self.player.position).angle
        return CmdBuilder().addMoveTo(Pose(self.player.position + latteral_move, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=False).addChargeKicker().build()

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def get_destination_behind_ball(self, ball_spacing, velocity=True, velocity_offset=25) -> Position:
        """
         Compute the point which is at ball_spacing mm behind the ball from the target.
        """

        dir_ball_to_target = normalize(self.game_state.ball.velocity)

        position_behind = self.game_state.ball.position - dir_ball_to_target * ball_spacing

        if velocity:
            position_behind += (self.game_state.ball.velocity - (normalize(self.game_state.ball.velocity) *
                                                                 np.dot(dir_ball_to_target.array,
                                                                        self.game_state.ball.velocity.array))) / velocity_offset

        return position_behind

    def is_ball_going_to_collide(self, threshold=18): # threshold in degrees
        ball_approach_angle = np.arccos(np.dot(normalize(self.player.position - self.game_state.ball.position).array,
                                               normalize(self.game_state.ball.velocity).array)) * 180 / np.pi
        return ball_approach_angle > threshold

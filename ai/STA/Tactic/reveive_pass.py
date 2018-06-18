# Under MIT licence, see LICENCE.txt

import math as m
import time
from typing import List, Union

import numpy as np

from Util.constant import ROBOT_CENTER_TO_KICKER, BALL_RADIUS, KickForce
from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle
from Util.geometry import compare_angle, normalize
from ai.Algorithm.evaluation_module import best_passing_option, player_covered_from_goal
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


GO_BEHIND_SPACING = 250
GRAB_BALL_SPACING = 100
HAS_BALL_DISTANCE = 130
KICK_SUCCEED_THRESHOLD = 300


# noinspection PyArgumentList,PyUnresolvedReferences,PyUnresolvedReferences
class ReceivePass(Tactic):
    def __init__(self, game_state: GameState, player: Player):

        super().__init__(game_state, player)
        self.current_state = self.initialize
        self.next_state = self.initialize

    def initialize(self):
        self.status_flag = Flags.WIP
        if self.is_ball_going_to_collide():
            if self.game_state.ball.velocity.norm < 100:
                self.next_state = self.grab_ball
            else:
                self.next_state = self.wait_for_ball
        else:
            self.next_state = self.go_behind_ball

        return Idle

    def go_behind_ball(self):
        orientation = (self.game_state.ball_position - self.player.position).angle
        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_modifier = (ball_speed/1000 + 1)
        effective_ball_spacing = GRAB_BALL_SPACING * 3 * ball_speed_modifier
        distance_behind = self.get_destination_behind_ball(effective_ball_spacing)
        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        if self.is_ball_going_to_collide(threshold=0.95) \
                and compare_angle(self.player.pose.orientation, orientation,
                                  abs_tol=max(0.1, 0.1 * dist_from_ball/100)):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=True)\
                           .addChargeKicker().build()

    def grab_ball(self):
        if not self.is_ball_going_to_collide(threshold=0.95):
            self.next_state = self.go_behind_ball

        if self._get_distance_from_ball() < HAS_BALL_DISTANCE:
            self.next_state = self.halt
            return self.halt()
        orientation = (self.game_state.ball_position - self.player.position).angle
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=False).addForceDribbler().build()

    def wait_for_ball(self):
        if self._get_distance_from_ball() < HAS_BALL_DISTANCE:
            self.next_state = self.halt
            return self.halt()
        if not self.is_ball_going_to_collide(threshold=0.95):
            self.next_state = self.go_behind_ball
            return CmdBuilder().build()
        orientation = (self.game_state.ball_position - self.player.position).angle
        return CmdBuilder().addMoveTo(Pose(self.player.position, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=False).addForceDribbler().build()

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.initialize
        else:
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

    def is_ball_going_to_collide(self, threshold=0.95):

        return np.dot(normalize(self.player.position - self.game_state.ball.position).array,
                      normalize(self.game_state.ball.velocity).array) > threshold

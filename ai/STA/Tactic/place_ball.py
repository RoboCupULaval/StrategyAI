# Under MIT licence, see LICENCE.txt

import math as m
import time
from typing import List, Union

import numpy as np

from Util.constant import ROBOT_CENTER_TO_KICKER, BALL_RADIUS, KickForce
from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle
from Util.geometry import compare_angle, normalize
from ai.Algorithm.evaluation_module import best_passing_option
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from ai.Algorithm.evaluation_module import is_ball_outside_field, is_ball_near_wall

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 20
APPROACH_SPEED = 100
KICK_DISTANCE = 100
KICK_SUCCEED_THRESHOLD = 600
COMMAND_DELAY = 0.5
SUCCESS_THRESHOLD = 300

# noinspection PyArgumentList,PyUnresolvedReferences,PyUnresolvedReferences
class PlaceBall(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: KickForce=KickForce.MEDIUM,
                 auto_update_target=False,
                 go_behind_distance=GRAB_BALL_SPACING*3):

        super().__init__(game_state, player, target, args)
        self.fetch_ball()
        self.cmd_last_time = time.time()
        self.kick_last_time = time.time()
        self.target = target
        self.go_behind_distance = go_behind_distance
        self.tries_flag = 0
        self.grab_ball_tries = 0
        self.steady_orrientation = self.player.pose.orientation
        self.time = time.time()
        self.ball_position = self.game_state.ball_position

    def fetch_ball(self):
        if is_ball_outside_field():
            self.next_state = self.halt
        else:
            if is_ball_near_wall():
                self.next_state = self.go_in_front_ball
            else:
                self.next_state = self.go_behind_ball

    def go_behind_ball(self):
        self.fetch_ball()
        self.ball_position = self.game_state.ball_position
        self.status_flag = Flags.WIP

        orientation = (self.target.position - self.player.pose.position).angle

        distance_behind = self.get_destination_behind_ball(self.go_behind_distance)

        if (self.player.pose.position - distance_behind).norm < 50 \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
        # ball_collision = self.tries_flag == 0
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=2,
                                      end_speed=0,
                                      ball_collision=True).build()

    def go_in_front_ball(self):
        self.fetch_ball()
        self.ball_position = self.game_state.ball_position
        self.status_flag = Flags.WIP
        orientation = (self.target.position - self.player.pose.position).angle - np.pi

        distance_in_front = self.get_destination_behind_ball(-1 * self.go_behind_distance)

        if (self.player.pose.position - distance_in_front).norm < 50 \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.time = time.time()
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_in_front_ball
        # ball_collision = self.tries_flag == 0
        return CmdBuilder().addMoveTo(Pose(distance_in_front, orientation),
                                      cruise_speed=2,
                                      end_speed=0,
                                      ball_collision=True).build()

    def grab_ball(self):

        if self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10) or self.time - time.time() > 5:
            self.next_state = self.move_ball

        orientation = (self.target.position - self.player.pose.position).angle
        if is_ball_near_wall():
            orientation -= np.pi
            distance_behind = self.get_destination_behind_ball(-GRAB_BALL_SPACING)
        else:
            distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        self.steady_orrientation = orientation
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=1,
                                      ball_collision=False).addChargeKicker().addForceDribbler().build()

    def move_ball(self):
        self.ball_position = self.game_state.ball_position
        if self.check_success():
            self.next_state = self.halt
        elif (self.player.pose.position - self.ball_position).norm > 300:
            self.fetch_ball()
            return CmdBuilder().build()
        else:
            return CmdBuilder().addMoveTo(Pose(self.target.position, self.steady_orrientation),
                                          cruise_speed=0.5,
                                          ball_collision=False).addForceDribbler().build()
        return CmdBuilder().build()

    def check_success(self):
        return (self.game_state.ball_position - self.target.position).norm < SUCCESS_THRESHOLD

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.fetch_ball()
        else:
            self.status_flag = Flags.SUCCESS
        return Idle

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.ball_position).norm

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi/30):
        ball_position = self.game_state.ball_position
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle, ball_to_player.angle, abs_tol=abs_tol)

    def get_destination_behind_ball(self, ball_spacing) -> Position:
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """
        delta_x = self.target.position.x - self.ball_position.x
        delta_y = self.target.position.y - self.ball_position.y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.ball_position.x - ball_spacing * np.math.cos(theta)
        y = self.ball_position.y - ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position


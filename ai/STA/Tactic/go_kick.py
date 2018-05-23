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

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 100
APPROACH_SPEED = 100
KICK_DISTANCE = 130
KICK_SUCCEED_THRESHOLD = 600
COMMAND_DELAY = 0.5


# noinspection PyArgumentList,PyUnresolvedReferences,PyUnresolvedReferences
class GoKick(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: KickForce=KickForce.MEDIUM,
                 auto_update_target=False,
                 go_behind_distance=GRAB_BALL_SPACING*3):

        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.cmd_last_time = time.time()
        self.kick_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.target_assignation_last_time = 0
        self.target = target
        if self.auto_update_target:
            self._find_best_passing_option()
        self.kick_force = kick_force
        self.go_behind_distance = go_behind_distance
        self.tries_flag = 0
        self.grab_ball_tries = 0

    def kick_charge(self):
        if time.time() - self.cmd_last_time > COMMAND_DELAY:
            self.next_state = self.go_behind_ball
            self.cmd_last_time = time.time()

        return CmdBuilder().addChargeKicker().build()

    def go_behind_ball(self):
        self.status_flag = Flags.WIP
        orientation = (self.target.position - self.player.pose.position).angle
        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_modifier = (ball_speed/1000 + 1)

        distance_behind = self.get_destination_behind_ball(self.go_behind_distance * ball_speed_modifier)

        if (self.player.pose.position - distance_behind).norm < 50 \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            if self.auto_update_target:
                self._find_best_passing_option()
        # ball_collision = self.tries_flag == 0
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=2,
                                      end_speed=0,
                                      ball_collision=True).build()

    def grab_ball(self):
        if self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10):
            self.next_state = self.kick

        orientation = (self.target.position - self.player.pose.position).angle
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=1,
                                      ball_collision=False).addChargeKicker().build()

    def kick(self):
        self.next_state = self.validate_kick
        self.tries_flag += 1

        player_to_target = (self.target.position - self.player.pose.position)
        behind_ball = self.game_state.ball_position - normalize(player_to_target) * (BALL_RADIUS + ROBOT_CENTER_TO_KICKER)
        orientation = player_to_target.angle

        return CmdBuilder().addMoveTo(Pose(behind_ball, orientation)).addKick(self.kick_force).build()

    def validate_kick(self):
        if self.game_state.ball_velocity.norm > 1000 or self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.kick
        else:
            self.status_flag = Flags.INIT
            self.next_state = self.go_behind_ball

        return CmdBuilder().build()

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi/30):
        ball_position = self.game_state.ball_position
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle, ball_to_player.angle, abs_tol=abs_tol)

    def _find_best_passing_option(self):
        assignation_delay = (time.time() - self.target_assignation_last_time)

        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose.from_values(GameState().field.their_goal_x, 0, 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing) -> Position:
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """
        delta_x = self.target.position.x - self.game_state.ball_position.x
        delta_y = self.target.position.y - self.game_state.ball_position.y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.game_state.ball_position.x - ball_spacing * np.math.cos(theta)
        y = self.game_state.ball_position.y - ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position

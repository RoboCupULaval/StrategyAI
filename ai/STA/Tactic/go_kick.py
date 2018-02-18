# Under MIT licence, see LICENCE.txt

import math as m
import time
from typing import List, Union

import numpy as np

from Util import Pose, Position, AICommand
from Util.geometry import compare_angle
from ai.Algorithm.evaluation_module import best_passing_option
from ai.GameDomainObjects import Player
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.kick_charge import KickCharge
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 100
APPROACH_SPEED = 100
KICK_DISTANCE = 110
KICK_SUCCEED_THRESHOLD = 600
COMMAND_DELAY = 0.5


class GoKick(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: Union[int, float]=5,
                 auto_update_target=False):

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
        self.ball_spacing = GRAB_BALL_SPACING
        self.tries_flag = 0
        self.grab_ball_tries = 0

    def kick_charge(self):
        if time.time() - self.cmd_last_time > COMMAND_DELAY:
            self.next_state = self.go_behind_ball
            self.cmd_last_time = time.time()

        # todo charge kick here please/ask Simon what kicktype is supposed to be
        return KickCharge(self.game_state, self.player, kick_type=1)

    def go_behind_ball(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.status_flag = Flags.WIP
        self.player.ball_collision = True
        orientation = (self.target.position - self.player.pose.position).angle()
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING * 3)
        if (self.player.pose.position - distance_behind).norm() < 50:
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            if self.auto_update_target:
                self._find_best_passing_option()
        collision_ball = self.tries_flag == 0
        return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                      collision_ball=collision_ball, cruise_speed=1)

    def grab_ball(self):
        self.player.ball_collision = False
        if self.grab_ball_tries == 0:
            if self._get_distance_from_ball() < KICK_DISTANCE:
                self.next_state = self.kick
        else:
            if self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10):
                self.next_state = self.kick

        orientation = (self.target.position - self.player.pose.position).angle()
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                     cruise_speed=2, charge_kick=True, end_speed=0)

    def kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.next_state = self.validate_kick
        self.tries_flag += 1
        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - self.player.pose.position).angle()
        return Kick(self.game_state, self.player, self.kick_force, Pose(ball_position, orientation), cruise_speed=2, end_speed=0)

    def validate_kick(self):
        if self.game_state.get_ball_velocity().norm() > 1000 or self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.kick
        else:
            self.status_flag = Flags.INIT
            self.next_state = self.go_behind_ball

        return Idle(self.game_state, self.player)

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi/30):
        ball_position = self.game_state.get_ball_position()
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle(), ball_to_player.angle(), abs_tol=abs_tol)

    def _find_best_passing_option(self):
        assignation_delay = (time.time() - self.target_assignation_last_time)

        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0, 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing):
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """

        delta_x = self.target.position.x - self.game_state.get_ball_position().x
        delta_y = self.target.position.y - self.game_state.get_ball_position().y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.game_state.get_ball_position().x - ball_spacing * np.math.cos(theta)
        y = self.game_state.get_ball_position().y - ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position

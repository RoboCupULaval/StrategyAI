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

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 0.5

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 100
APPROACH_SPEED = 100
KICK_DISTANCE = 130
KICK_SUCCEED_THRESHOLD = 300
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
        self.current_state = self.initialize
        self.next_state = self.initialize
        self.kick_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.target_assignation_last_time = 0
        self.target = target
        if self.auto_update_target:
            self._find_best_passing_option()
        self.kick_force = kick_force
        self.go_behind_distance = go_behind_distance

    def initialize(self):
        orientation = (self.target.position - self.game_state.ball_position).angle

        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        if self.is_able_to_grab_ball_directly(0.3) \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=max(0.1, 0.1 * dist_from_ball/100)):
            self.next_state = self.grab_ball
            if self._get_distance_from_ball() < KICK_DISTANCE:
                self.next_state = self.kick

        else:
            self.next_state = self.go_behind_ball

        return Idle

    def go_behind_ball(self):
        self.status_flag = Flags.WIP
        orientation = (self.target.position - self.game_state.ball_position).angle
        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_modifier = (ball_speed/1000 + 1)
        effective_ball_spacing = GRAB_BALL_SPACING * 3 * ball_speed_modifier
        distance_behind = self.get_destination_behind_ball(effective_ball_spacing)
        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        if self.is_able_to_grab_ball_directly(0.7) \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=max(0.1, 0.1 * dist_from_ball/100)):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            if self.auto_update_target:
                self._find_best_passing_option()
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=2,
                                      end_speed=0,
                                      ball_collision=True)\
                           .addChargeKicker().build()

    def grab_ball(self):

        vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        if not self.is_able_to_grab_ball_directly(0.7):
            self.next_state = self.go_behind_ball

        if self._get_distance_from_ball() < KICK_DISTANCE:
            self.next_state = self.kick
            self.kick_last_time = time.time()

        orientation = (self.target.position - self.game_state.ball_position).angle
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=1,
                                      ball_collision=False).addChargeKicker().build()

    def kick(self):
        self.next_state = self.validate_kick

        player_to_target = (self.target.position - self.player.pose.position)
        behind_ball = self.game_state.ball_position - normalize(player_to_target) * (BALL_RADIUS + ROBOT_CENTER_TO_KICKER)
        orientation = (self.target.position - self.game_state.ball_position).angle

        return CmdBuilder().addMoveTo(Pose(behind_ball, orientation),
                                      ball_collision=False).addKick(self.kick_force).build()

    def validate_kick(self):
        if self.game_state.ball.is_moving_fast() or self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.kick
        else:
            self.status_flag = Flags.INIT
            self.next_state = self.go_behind_ball

        return CmdBuilder().build()

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.initialize
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
        scoring_target = player_covered_from_goal(self.player)
        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if scoring_target is not None:
                self.target = Pose(scoring_target, 0)
            elif tentative_target_id is None:
                self.target = Pose(self.game_state.field.their_goal, 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing) -> Position:
        """
         Compute the point which is at ball_spacing mm behind the ball from the target.
        """
        dir_ball_to_target = normalize(self.target.position - self.game_state.ball.position)

        return self.game_state.ball.position - dir_ball_to_target * ball_spacing

    def is_able_to_grab_ball_directly(self, threshold):
        # plus que le threshold est gors (1 max), plus qu'on veut que le robot soit direct deriere la balle.
        vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        alignement_behind = np.dot(vec_target_to_ball.array,
                                   (normalize(self.player.position - self.game_state.ball_position)).array)

        return threshold < alignement_behind

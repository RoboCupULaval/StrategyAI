# Under MIT licence, see LICENCE.txt

import time
from typing import List

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory, CYAN, RED
from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle
from Util.constant import ROBOT_CENTER_TO_KICKER, KickForce
from Util.geometry import compare_angle, normalize
from ai.Algorithm.evaluation_module import best_passing_option, player_covered_from_goal
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from config.config import Config

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1.0

MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_TO_PASS = 2
MIN_NB_CONSECUTIVE_DECISIONS_TO_SWITCH_FROM_PASS = 5

GO_BEHIND_SPACING = 180
GRAB_BALL_SPACING = 90
APPROACH_SPEED = 100
KICK_DISTANCE = 130
KICK_SUCCEED_THRESHOLD = 300
COMMAND_DELAY = 0.5


class GoKick(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose = Pose(),
                 args: List[str] = None,
                 kick_force: KickForce = KickForce.HIGH,
                 auto_update_target=False,
                 go_behind_distance=GRAB_BALL_SPACING * 3,
                 forbidden_areas=None,
                 can_kick_in_goal=False):

        super().__init__(game_state, player, target, args=args, forbidden_areas=forbidden_areas)
        self.current_state = self.initialize
        self.next_state = self.initialize
        self.kick_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.can_kick_in_goal = can_kick_in_goal
        self.target_assignation_last_time = 0
        self.target = target

        self.current_player_target = None
        self.nb_consecutive_times_a_pass_is_decided = 0
        self.nb_consecutive_times_a_pass_is_not_decided = 0

        self.kick_force = kick_force
        self.go_behind_distance = go_behind_distance

        self.is_debug = True

    def initialize(self):
        if self.auto_update_target:
            self._find_best_passing_option()
        required_orientation = (self.target.position - self.game_state.ball_position).angle

        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        if self.get_alignment_with_ball_and_target() < 60 \
                and compare_angle(self.player.pose.orientation,
                                  required_orientation,
                                  abs_tol=max(0.1, 0.1 * dist_from_ball / 1000)) or not self.is_able_to_grab_ball_directly(0.7):
            self.next_state = self.go_behind_ball
            if self._get_distance_from_ball() < KICK_DISTANCE:
                self.next_state = self.kick

        else:
            self.next_state = self.go_behind_ball

        return Idle

    def go_behind_ball(self):
        if self.auto_update_target:
            self._find_best_passing_option()
        self.status_flag = Flags.WIP
        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        required_orientation = (self.target.position - self.game_state.ball_position).angle
        ball_speed = self.game_state.ball.velocity.norm
        angle_behind = self.get_alignment_with_ball_and_target()
        if angle_behind > 35:
            effective_ball_spacing = GO_BEHIND_SPACING
            collision_ball = True
        else:
            effective_ball_spacing = GO_BEHIND_SPACING
            collision_ball = False
            if compare_angle(self.player.pose.orientation, required_orientation,
                             abs_tol=max(0.05, 0.05 * dist_from_ball / 1000)):
                self.next_state = self.grab_ball
            else:
                self.next_state = self.go_behind_ball
        position_behind_ball = self.get_destination_behind_ball(effective_ball_spacing)

        if angle_behind > 70 and dist_from_ball < 1000:
            cruise_speed = 1 + ball_speed / 1000
        else:
            cruise_speed = 3

        return CmdBuilder().addMoveTo(Pose(position_behind_ball, required_orientation),
                                      cruise_speed=cruise_speed,
                                      end_speed=0,
                                      ball_collision=collision_ball)\
                           .addChargeKicker().addKick(self.kick_force).build()

    def grab_ball(self):
        if self.auto_update_target:
            self._find_best_passing_option()
        angle_behind = self.get_alignment_with_ball_and_target()
        if angle_behind > 35:
            self.next_state = self.go_behind_ball

        if self._get_distance_from_ball() < KICK_DISTANCE:
            self.next_state = self.kick
            self.kick_last_time = time.time()
        ball_speed = self.game_state.ball.velocity.norm
        required_orientation = (self.target.position - self.game_state.ball_position).angle
        position_behind_ball = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return CmdBuilder().addMoveTo(Pose(position_behind_ball, required_orientation), ball_collision=False)\
                           .addForceDribbler()\
                           .addKick(self.kick_force)\
                           .build()

    def kick(self):
        if self.auto_update_target:
            self._find_best_passing_option()
        if self.get_alignment_with_ball_and_target() > 45:
            self.next_state = self.go_behind_ball
            return self.go_behind_ball()
        self.next_state = self.validate_kick

        player_to_target = (self.target.position - self.player.pose.position)
        position_behind_ball = self.game_state.ball_position + normalize(player_to_target) * ROBOT_CENTER_TO_KICKER
        required_orientation = (self.target.position - self.game_state.ball_position).angle
        if self.player.id not in Config()["COACH"]["working_kicker_ids"]:
            player_to_ball = normalize(self.game_state.ball_position - self.player.pose.position)
            ram_position = Pose(player_to_ball*100+self.game_state.ball_position, required_orientation)
            return CmdBuilder().addMoveTo(ram_position,
                                          ball_collision=False,
                                          cruise_speed=3,
                                          end_speed=2).build()
        else:
            return CmdBuilder().addMoveTo(Pose(position_behind_ball, required_orientation), ball_collision=False)\
                                            .addKick(self.kick_force)\
                                            .addForceDribbler().build()

    def validate_kick(self):
        if self.game_state.ball.is_moving_fast() and self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
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

    def get_destination_behind_ball(self, ball_spacing, velocity=True, velocity_offset=4) -> Position:
        """
         Compute the point which is at ball_spacing mm behind the ball from the target.
        """

        dir_ball_to_target = normalize(self.target.position - self.game_state.ball.position)

        position_behind = self.game_state.ball.position - dir_ball_to_target * ball_spacing

        if velocity and self.game_state.ball.velocity.norm > 20:
            position_behind += (self.game_state.ball.velocity -
                                (normalize(self.game_state.ball.velocity) *
                                 np.dot(dir_ball_to_target.array,
                                        self.game_state.ball.velocity.array))) / velocity_offset

        return position_behind

    def get_alignment_with_ball_and_target(self):
        # TODO CE NORMALIZE PEUT RAISE UNE DIVISION PAR 0
        vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        alignement_behind = np.dot(vec_target_to_ball.array,
                                   (normalize(self.player.position - self.game_state.ball_position)).array)
        return np.arccos(alignement_behind) * 180 / np.pi

    def debug_cmd(self):

        if not self.is_debug:
            return []

        angle = None
        additional_dbg = []
        if self.current_state == self.go_behind_ball:
            angle = 18
        elif self.current_state == self.grab_ball:
            angle = 25
        elif self.current_state == self.kick:
            angle = 45
            additional_dbg = [DebugCommandFactory.circle(self.game_state.ball_position, KICK_DISTANCE, color=RED)]
        if angle is not None:
            angle *= np.pi / 180.0
            base_angle = (self.game_state.ball.position - self.target.position).angle
            magnitude = 3000
            ori = self.game_state.ball.position
            upper = ori - Position.from_angle(base_angle + angle, magnitude)
            lower = ori - Position.from_angle(base_angle - angle, magnitude)
            ball_to_player = self.player.position - self.game_state.ball_position
            behind_player = (ball_to_player.norm + 1000) * normalize(ball_to_player) + self.game_state.ball_position
            return [DebugCommandFactory.line(ori, upper),
                    DebugCommandFactory.line(ori, lower),
                    DebugCommandFactory.line(self.game_state.ball_position, behind_player, color=CYAN)] + additional_dbg
        return []

    def is_able_to_grab_ball_directly(self, threshold):
        # plus que le threshold est gors (1 max), plus qu'on veut que le robot soit direct deriere la balle.
        try:
            vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        except ZeroDivisionError:
            vec_target_to_ball = Position(0, 0)  # In case we have no positional error

        try:
            player_to_ball = (normalize(self.player.position - self.game_state.ball_position)).array
        except ZeroDivisionError:
            player_to_ball = Position(0, 0)  # In case we have no positional error

        alignement_behind = np.dot(vec_target_to_ball.array, player_to_ball)
        return threshold < alignement_behind

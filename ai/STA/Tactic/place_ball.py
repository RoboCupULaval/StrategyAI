# Under MIT licence, see LICENCE.txt

import time
from typing import List

from Util.constant import ROBOT_CENTER_TO_KICKER, ROBOT_DIAMETER, KEEPOUT_DISTANCE_FROM_BALL
from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle
from Util.geometry import compare_angle, normalize, random_direction
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from config.config import Config


GRAB_BALL_SPACING = 20
GO_BEHIND_SPACING = GRAB_BALL_SPACING * 10
TOLERANCE_ON_BALL_FINAL_POSITION = 100

BALL_DISPLACEMENT_TO_DETECT_GRABBING = 20
TIME_TO_WAIT_FOR_BALL_STOP_MOVING = 2  # secondes


# noinspection PyArgumentList
class PlaceBall(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 go_behind_distance=GO_BEHIND_SPACING):

        super().__init__(game_state, player, target, args, forbidden_areas=[])
        self.target = target
        self.go_behind_distance = go_behind_distance

        # The simulation dribbler does not back spin as much as in real life
        self.move_ball_cruise_speed = 0.1 if Config().is_simulation() else 0.3

        self._fetch_ball()

        self.wait_timer = None
        self.position_ball_at_start = None
        self.player_target_position = None
        self.steady_orientation = None

    def _fetch_ball(self):
        if self.game_state.field.is_outside_wall_limit(self.game_state.ball_position) or self._check_success():
            self.next_state = self.halt
        else:
            self.next_state = self.go_behind_ball

    def halt(self):
        if self.status_flag == Flags.INIT:
            self._fetch_ball()
        return Idle

    def go_behind_ball(self):
        self.status_flag = Flags.WIP

        orientation = (self.game_state.ball.position - self.target.position).angle

        distance_behind = self._get_destination_behind_ball(self.go_behind_distance)

        if (self.player.pose.position - distance_behind).norm < 200 \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):
            self.next_state = self.grab_ball

        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=1,
                                      ball_collision=True).build()

    def grab_ball(self):
        if self.position_ball_at_start is None:
            self.position_ball_at_start = self.game_state.ball_position.copy()
        orientation = (self.game_state.ball.position - self.target.position).angle
        distance_behind = self._get_destination_behind_ball(GRAB_BALL_SPACING)

        if (self.position_ball_at_start - self.game_state.ball.position).norm > BALL_DISPLACEMENT_TO_DETECT_GRABBING \
                and compare_angle(self.player.pose.orientation, orientation, abs_tol=0.3):
            self.next_state = self.move_ball
            self.position_ball_at_start = None
            self.steady_orientation = orientation

        return CmdBuilder().addMoveTo(Pose(distance_behind, orientation),
                                      cruise_speed=0.2,
                                      ball_collision=False).addForceDribbler().build()

    def move_ball(self):
        if self._check_success():
            self.next_state = self.wait_for_ball_stop_spinning
        elif self._has_ball_quit_dribbler():
            self._fetch_ball()
        ball_position = self.game_state.ball_position
        ball_to_target_dir = normalize(self.target.position - ball_position)
        self.player_target_position = ROBOT_CENTER_TO_KICKER * ball_to_target_dir + self.target.position

        return CmdBuilder().addMoveTo(Pose(self.player_target_position, self.steady_orientation),
                                      cruise_speed=self.move_ball_cruise_speed,
                                      ball_collision=False).addForceDribbler().build()

    def wait_for_ball_stop_spinning(self):
        if self.wait_timer is None:
            self.wait_timer = time.time()

        if time.time() - self.wait_timer > TIME_TO_WAIT_FOR_BALL_STOP_MOVING:
            self.next_state = self.get_away_from_ball
            self.wait_timer = None
        if self._has_ball_quit_dribbler():
            self._fetch_ball()
        return CmdBuilder().addMoveTo(Pose(self.player_target_position, self.steady_orientation),
                                      ball_collision=False).addStopDribbler().build()

    def get_away_from_ball(self):
        if self._check_success() and self._get_distance_from_ball() > KEEPOUT_DISTANCE_FROM_BALL:
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS

        target_to_player = normalize(self.player.position - self.target.position)
        pos_away_from_ball = 1.2 * KEEPOUT_DISTANCE_FROM_BALL * target_to_player + self.target.position
        # Move to a position away from ball
        return CmdBuilder().addMoveTo(Pose(pos_away_from_ball,
                                           self.player.orientation)).addStopDribbler().build()

    def _has_ball_quit_dribbler(self):
        return (self.player.pose.position - self.game_state.ball.position).norm > 300

    def _check_success(self):
        return (self.game_state.ball_position - self.target.position).norm < TOLERANCE_ON_BALL_FINAL_POSITION

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _get_destination_behind_ball(self, ball_spacing) -> Position:
        direction = self.target.position - self.game_state.ball.position
        return ball_spacing * normalize(direction) + self.game_state.ball.position



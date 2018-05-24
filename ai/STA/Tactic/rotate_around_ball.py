# Under MIT licence, see LICENCE.txt

import time
from typing import Optional, List

import numpy as np

from Util import Pose, Position
from Util.ai_command import Idle, CmdBuilder
from Util.geometry import compare_angle, find_signed_delta_angle
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

DIFF_ANGLE = 0.2
DISTANCE_FROM_BALL = 400
VALID_DISTANCE = 250
VALID_DIFF_ANGLE = 0.15


class RotateAroundBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose,
                 args: Optional[List[str]] = None, rotate_time=4, switch_time=1.5):
        super().__init__(game_state, player, target, args)
        self.rotate_time = rotate_time
        self.switch_time = switch_time
        self.current_state = self.next_position
        self.next_state = self.next_position
        self.target = target

        self.start_time = time.time()
        self.iter_time = time.time()

        self.ball_position = self.game_state.ball_position
        self.target_orientation = (self.target.position - self.ball_position).angle
        self.start_orientation = (self.ball_position - self.player.position).angle

        self.offset_orientation = self.start_orientation

        self.position = (self.game_state.ball_position - Position.from_angle(self.offset_orientation) * DISTANCE_FROM_BALL)
        self.rotation = self.get_direction()

    def next_position(self):
        if time.time() - self.start_time >= self.rotate_time:
            self.rotation = self.get_direction()
            if compare_angle(self.target_orientation, (self.ball_position - self.player.position).angle, VALID_DIFF_ANGLE):
                self.next_state = self.halt
                return Idle
        elif time.time() - self.iter_time >= self.switch_time:
            self.iter_time = time.time()
            self.switch_rotation()
        if (self.player.pose.position - self.position).norm < VALID_DISTANCE:
            self.offset_orientation += DIFF_ANGLE * self.rotation
            self.position = (self.game_state.ball_position - Position.from_angle(self.offset_orientation) * DISTANCE_FROM_BALL)
        return CmdBuilder().addMoveTo(Pose(self.position, self.offset_orientation),
                                      cruise_speed=1, end_speed=1,
                                      ball_collision=False).build()

    def switch_rotation(self):
        self.rotation *= -1
        self.offset_orientation += 2 * DIFF_ANGLE * self.rotation

    def get_direction(self):
        return np.sign(find_signed_delta_angle(self.target_orientation, self.offset_orientation))

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle

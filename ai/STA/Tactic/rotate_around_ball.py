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
        self.ball_collision = True
        self.speed = 2

        self.start_time = None
        self.iter_time = None

        self.target_orientation = None
        self.offset_orientation = (self.game_state.ball_position - self.player.position).angle
        self.rotation_sign = self._get_direction()

        self.position = Position

    def next_position(self):
        self.target_orientation = (self.target.position - self.game_state.ball_position).angle
        self.position = (self.game_state.ball_position - Position.from_angle(self.offset_orientation) * DISTANCE_FROM_BALL)
        if self.start_time is not None:
            if time.time() - self.start_time >= self.rotate_time:
                self.rotation_sign = self._get_direction()
                if compare_angle(self.target_orientation, (self.game_state.ball_position - self.player.position).angle, VALID_DIFF_ANGLE):
                    self.next_state = self.halt
                    return self._go_to_final_position()
            elif time.time() - self.iter_time >= self.switch_time:
                self.iter_time = time.time()
                self._switch_rotation()

        if (self.player.pose.position - self.position).norm < VALID_DISTANCE:
            if self.start_time is None:
                self.start_time = time.time()
                self.iter_time = time.time()
                self.ball_collision = True
                self.speed = 1
            self.offset_orientation += DIFF_ANGLE * self.rotation_sign
            self.position = (self.game_state.ball_position - Position.from_angle(self.offset_orientation) * DISTANCE_FROM_BALL)

        if self.start_time is not None:
            orientation = self.offset_orientation if time.time() - self.start_time < self.rotate_time else self.target_orientation
        else:
            orientation = self.target_orientation
        return CmdBuilder().addMoveTo(Pose(self.position, orientation),
                                      cruise_speed=self.speed,
                                      ball_collision=self.ball_collision).build()

    def _switch_rotation(self):
        self.rotation_sign *= -1
        self.offset_orientation += 2 * DIFF_ANGLE * self.rotation_sign

    def _get_direction(self):
        return np.sign(find_signed_delta_angle(self.target_orientation, self.offset_orientation))

    def _go_to_final_position(self):
        position = self.game_state.ball_position - Position.from_angle(self.target_orientation) * DISTANCE_FROM_BALL
        return CmdBuilder().addMoveTo(Pose(position, self.target_orientation),
                               cruise_speed=self.speed,
                               ball_collision=self.ball_collision).build()

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return self._go_to_final_position()

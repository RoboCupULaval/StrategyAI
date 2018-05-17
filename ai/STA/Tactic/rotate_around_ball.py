# Under MIT licence, see LICENCE.txt

import time
from typing import Optional, List

from Util import Pose, Position
from Util.ai_command import Idle, CmdBuilder
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState
import random


class RotateAroundBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: Optional[List[str]] = None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.next_position
        self.next_state = self.next_position
        self.target = target

        self.start_time = time.time()
        self.switch_time = time.time()

        self.ball_position = self.game_state.ball_position
        self.target_orientation = (self.target.position - self.ball_position).angle
        self.offset_orientation = self.target_orientation
        self.position = (self.game_state.ball_position - Position.from_angle(self.offset_orientation) * 400)
        self.rotation = -1

    def next_position(self):
        if time.time() - self.start_time >= 30:
            #self.next_state = self.halt()
            pass
        if time.time() - self.switch_time >= 3:
            self.switch_time = time.time()
            self.switch_rotation()
        elif (self.player.pose.position - self.position).norm < 250:
            self.offset_orientation += .2 * self.rotation
            self.position = (self.game_state.ball_position - Position.from_angle(self.offset_orientation)*400)
        return CmdBuilder().addMoveTo(Pose(self.position, self.offset_orientation),
                                      cruise_speed=1.5, end_speed=1.2,
                                      ball_collision=False).build()

    def switch_rotation(self):
        self.rotation *= -1
        self.offset_orientation += .4 * self.rotation

    def halt(self):
        return Idle

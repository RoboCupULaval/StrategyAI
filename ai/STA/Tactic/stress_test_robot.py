from typing import List

from Util import Position, Pose
from Util.ai_command import CmdBuilder
from Util.constant import ROBOT_RADIUS
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState

COORD_X = 3000
COORD_Y = 2000
VALID_DISTANCE = ROBOT_RADIUS * 0.5
CLOCKWISE = 1   # -1 for counter-clockwise
DEFAULT_SPEED = 2


class StressTestRobot(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose,
                 args: List[str]=None, speed=DEFAULT_SPEED):
        super().__init__(game_state, player, target, args)
        self.current_state = self.next_corner
        self.next_state = self.next_corner
        self.speed = speed
        self.iteration = 0
        self.x_sign = 1
        self.y_sign = 1

    def next_corner(self):
        position = Position(COORD_X * self.x_sign, COORD_Y * self.y_sign)
        orientation = (position - self.player.position).angle
        if (position - self.player.position).norm < VALID_DISTANCE:
            self._switch_signs()
        return CmdBuilder().addMoveTo(Pose(position, orientation), cruise_speed=self.speed).build()

    def _switch_signs(self):
        if self.x_sign * self.y_sign == CLOCKWISE:
            self.x_sign *= -1
        else:
            self.y_sign *= -1

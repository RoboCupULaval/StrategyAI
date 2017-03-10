# Under MIT license, see LICENSE.txt

import math as m
import pygame

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Move import Move
from ai.Util.joystick.joystick import RobotJoystick
from .Tactic import Tactic
from . tactic_constants import Flags


class Joystick(Tactic):
    def __init__(self, p_game_state, player_id, target):
        super().__init__(p_game_state, player_id, target)
        self.target = target
        self.status_flag = Flags.INIT
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()

        if player_id < joystick_count:
            pygame.display.set_mode([1, 1])
            joystick = pygame.joystick.Joystick(player_id)
            joystick.init()
            self.joy = RobotJoystick(joystick)
        else:
            self.status_flag = Flags.FAILURE


    def exec(self):
        if self.status_flag is not Flags.FAILURE:
            self.status_flag = Flags.WIP
            pygame.event.pump()

            x, y = self.joy.get_left_axis_vector()
            _, t = self.joy.get_right_axis_vector()

            speed_pose = Pose(Position(-y, x), t * -10)

            next_action = Move(self.game_state, self.player_id, speed_pose)
        else:
            next_action = Idle(self.game_state, self.player_id)

        return next_action.exec()

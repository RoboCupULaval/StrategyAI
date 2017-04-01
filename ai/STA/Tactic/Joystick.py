# Under MIT license, see LICENSE.txt

import math as m
import pygame

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Move import Move
from ai.Util.ai_command import AICommandType, AICommand
from ai.Util.joystick.joystick import RobotJoystick
from .Tactic import Tactic
from . tactic_constants import Flags


class Joystick(Tactic):
    def __init__(self, p_game_state, player_id, target=Pose(), args=None):
        super().__init__(p_game_state, player_id, target, args)
        self.target = target
        self.status_flag = Flags.INIT

        self.inv_x = int(args[0])
        self.inv_y = int(args[1])
        self.joy_id = int(args[2])

        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        if int(self.joy_id) < joystick_count:
            pygame.display.set_mode([1, 1])
            joystick = pygame.joystick.Joystick(self.joy_id)
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

            if self.joy.get_btn_value("X"):
                charge_kick = True
            else:
                charge_kick = False

            if self.joy.get_btn_value("A"):
                kick = 4
            else:
                kick = 0

            if self.joy.get_btn_value("B"):
                dribbler = 2
            else:
                dribbler = 0

            x_speed = -y * self.inv_y
            y_speed = x * self.inv_x

            speed_pose = Pose(Position(x_speed, y_speed), t * -5)

            if kick == 0:
                next_action = AICommand(self.player_id, AICommandType.MOVE,
                             **{"pose_goal": speed_pose, "speed_flag": True,
                                "charge_kick": charge_kick, "kick_strength": kick, "dribbler_on": dribbler})
            else:
                next_action = AICommand(self.player_id, AICommandType.KICK, **{"kick_strength" : kick})
        else:
            next_action = Idle(self.game_state, self.player_id).exec()

        return next_action

    def halt(self):
        pygame.quit()
        return super(Joystick, self).halt()

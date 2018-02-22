# Under MIT license, see LICENSE.txt

import math as m
from typing import Union

from Util import Pose
from Util.ai_command_shit import AICommand, AICommandType

from Util.ai_command_shit import AICommand, AICommandType
from Util.geometry import compare_angle, wrap_to_pi, rotate, normalized
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states.game_state import GameState

DEFAULT_ROTATION_SPEED = 6*m.pi  # rad/s
DEFAULT_RADIUS = 150  # mm


class RotateAround(Action):
    def __init__(self, game_state: GameState,
                 player: Player,
                 target: Pose,
                 radius: Union[int, float]=DEFAULT_RADIUS,
                 is_clockwise: Union[bool, None]=None,
                 aiming: Union[Pose, None]=None,
                 pathfinder_on=True,
                 speed_mode=False,
                 rotation_speed: Union[int, float]=DEFAULT_ROTATION_SPEED,
                 behind_target=None,
                 approach=False):
        """
            Rotate around the target position in the direction specify by is_clockwise flag.
            If a heading is provide, the robot will stop to rotate when it face the heading
            position around the target point.

            Warning: If the target is the ball and it stick to the dribbler, the robot will
            go backward since the robot cannot be at the right radius (Ball is moving with the robot)

            :param game_state: current game state
            :param player: Instance of the player (Player)
            :param target: Position of the center of rotation
            :param radius: Radius of the rotation around target position
            :param is_clockwise: Sense of rotation flag
            :param aiming: Desired facing direction of the robot at the target
        """
        Action.__init__(self, game_state, player)
        self.target = target
        self.radius = radius
        self.is_clockwise = is_clockwise
        self.aiming = aiming.position if aiming is not None else None
        self.pathfinder_on = pathfinder_on
        self.rotation_speed = rotation_speed
        self.behind_target = behind_target
        self.approach = approach
        self.approach_speed = 0.2
        if speed_mode:
            self.tangential_speed = self.rotation_speed * self.radius / 2.
        else:
            self.tangential_speed = 0

    def generate_destination(self):

        dt = self.game_state.get_delta_t()
        player = self.player.pose.position
        target = self.target.position
        target_to_player = player - target
        if not(self.behind_target is None):
            if (self.behind_target - self.player.pose.position).norm < 300:
                # print((self.behind_target - self.player.pose.position).norm())
                self.tangential_speed *= (self.behind_target - self.player.pose.position).norm / 300

        if self.aiming is not None:
            aiming_to_target = target - self.aiming
            heading_error = wrap_to_pi(aiming_to_target.angle - target_to_player.angle())
            if compare_angle(heading_error, 0, abs_tol=self.rotation_speed*dt/2):  # True if heading is right
                next_position = self.radius * aiming_to_target.normalized()
                next_orientation = aiming_to_target.angle - m.pi
                self.tangential_speed = 0
            else:
                if self.is_clockwise is None:  # Force the rotation in a specific orientation
                    delta_angle = m.copysign(self.rotation_speed * dt, heading_error)
                else:
                    delta_angle = m.copysign(self.rotation_speed * dt, -1 if self.is_clockwise else 1)
                next_position = self.radius * rotate(normalized(target_to_player), delta_angle)
                next_orientation = aiming_to_target.angle - m.pi

        else:  # If no aiming, we just rotate around the target with the target orientation
            delta_angle = m.copysign(self.rotation_speed * dt, -1 if self.is_clockwise else 1)
            next_position = self.radius * rotate(normalized(target_to_player), delta_angle)
            next_orientation = self.target.orientation + delta_angle / 2

        next_position += target

        return Pose(next_position, next_orientation)

    def exec(self):
        if self.approach:
            return AICommand(self.player,
                             AICommandType.MOVE,
                             pose_goal=self.generate_destination(),
                             pathfinder_on=self.pathfinder_on,
                             cruise_speed=self.approach_speed,
                             end_speed=self.tangential_speed)
        else:
            return AICommand(self.player,
                             AICommandType.MOVE,
                             pose_goal=self.generate_destination(),
                             pathfinder_on=self.pathfinder_on,
                             end_speed=self.tangential_speed)

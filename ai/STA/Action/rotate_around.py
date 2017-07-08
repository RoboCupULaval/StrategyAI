# Under MIT license, see LICENSE.txt

import math as m

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import compare_angle, wrap_to_pi

from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

from typing import Union

ROTATION_SPEED = 6*m.pi  # rad/s


class RotateAround(Action):
    def __init__(self, game_state: GameState,
                 player: OurPlayer,
                 target: Pose,
                 radius: Union[int, float],
                 is_clockwise: Union[bool]=None,
                 heading: Union[Pose, None]=None,
                 pathfinder_on=False):
        """
            :param game_state: current game state
            :param player: Instance of the player (OurPlayer)
            :param target: Position of the center of rotation
            :param radius: Radius of the rotation around target position
            :param is_clockwise: Sense of rotation flag.
        """
        Action.__init__(self, game_state, player)
        self.target = target
        self.radius = radius
        self.is_clockwise = is_clockwise
        self.heading = heading.position
        self.pathfinder_on = pathfinder_on

    def generate_destination(self):

        dt = self.game_state.get_delta_t()
        player = self.player.pose.position
        target = self.target.position
        target_to_player = player - target

        delta_angle = m.copysign(ROTATION_SPEED * dt, -1 if self.is_clockwise else 1)

        if self.heading is not None:
            heading_to_target = target - self.heading
            heading_error = wrap_to_pi(heading_to_target.angle() - target_to_player.angle())
            if compare_angle(heading_error, 0, abs_tol=abs(delta_angle)/2):  # True if heading is right
                next_position = self.radius * heading_to_target.normalized()
                next_orientation = heading_to_target.angle() - m.pi
            else:
                if self.is_clockwise is None:  # Force the rotation in a specific orientation
                    delta_angle = m.copysign(ROTATION_SPEED * dt, heading_error)
                next_position = self.radius * target_to_player.normalized().rotate(delta_angle)
                next_orientation = self.target.orientation + delta_angle / 2

        else:  # If no heading, we just rotate around the target with the target orientation
            next_position = self.radius * target_to_player.normalized().rotate(delta_angle)
            next_orientation = self.target.orientation + delta_angle / 2

        next_position += target

        return Pose(next_position, next_orientation)

    def exec(self):
        return AICommand(self.player,
                         AICommandType.MOVE,
                         pose_goal=self.generate_destination(),
                         pathfinder_on=self.pathfinder_on)

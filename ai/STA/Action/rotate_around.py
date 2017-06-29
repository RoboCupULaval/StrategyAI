# Under MIT license, see LICENSE.txt
import numpy as np
import math as m

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose

from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

from typing import Union


class RotateAround(Action):
    def __init__(self, game_state: GameState,
                 player: OurPlayer,
                 target: Pose,
                 radius: Union[int, float],
                 is_clockwise: bool=True):
        """
            :param game_state: current game state
            :param player: Instance of the player (OurPlayer)
            :param target: Position of the center of rotation
            :param radius: Radius of the rotation around target position
            :param is_clockwise: Sense of rotation flag
        """
        Action.__init__(self, game_state, player)
        self.target = target
        self.radius = radius
        self.is_clockwise = is_clockwise

    def generate_destination(self):

        player = self.player.pose.position
        target = self.target.position

        player_to_target = (target - player).normalized()

        delta_theta = m.copysign(m.pi/6, -1 if self.is_clockwise else 1)
        player_to_target_rot = -player_to_target.rotate(delta_theta)

        translation = player_to_target_rot * self.radius
        destination = translation + target

        return Pose(destination, player_to_target_rot.angle()-m.pi+m.pi/12)

    def exec(self):
        return AICommand(self.player, AICommandType.MOVE, pose_goal=self.generate_destination())

# Under MIT license, see LICENSE.txt
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose

from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

from typing import Union


class RotateAround(Action):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose, rayon: Union[int, float]):
        """
            :param game_state: current game state
            :param player: Instance of the player (OurPlayer)
            :param target: Position of the center of rotation
            :param rayon: Radius of the rotation around target position
        """
        Action.__init__(self, game_state, player)
        self.target = target
        self.game_state = game_state
        self.rayon = rayon

    def generate_destination(self):
        player = self.player.pose.position
        target = self.target.position
        player_to_target = target-player
        player_to_target_orientation = player_to_target.angle()
        target_orientation = self.target.orientation
        delta_theta = player_to_target_orientation - target_orientation
        delta_theta = min(abs(delta_theta), np.pi/6) * np.sign(delta_theta)
        player_to_ball_rot = -player_to_target.rotate(delta_theta)
        translation = player_to_ball_rot.normalized() * self.rayon
        destination = translation + target
        orientation = target_orientation
        return Pose(destination, orientation)

    def exec(self):
        return AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.generate_destination()})

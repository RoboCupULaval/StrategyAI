# Under MIT license, see LICENSE.txt
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType


class RotateAround(Action):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose, rayon: [int, float]):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui se déplace
            :param target: Pose du centre de rotation
            :param rayon: Distance entre le centre du robot et le centre de rotation
        """
        Action.__init__(self, game_state, player)
        self.target = target
        self.game_state = game_state
        self.rayon = rayon

    def generate_destination(self):
        player = self.player.pose.position.conv_2_np()
        target = self.target.position.conv_2_np()
        player_to_target_orientation = np.arctan2(target[1] - player[1], target[0] - player[0])
        target_orientation = self.target.orientation
        delta_theta = player_to_target_orientation - target_orientation
        delta_theta = min(abs(delta_theta), np.pi/6) * np.sign(delta_theta)
        rotation_matrix = np.array([[np.cos(delta_theta), np.sin(delta_theta)], [-np.sin(delta_theta), np.cos(delta_theta)]])
        player_to_ball_rot = np.dot(rotation_matrix, player - target)
        translation = player_to_ball_rot / np.linalg.norm(player_to_ball_rot) * self.rayon
        destination = translation + target
        orientation = target_orientation
        return Pose(Position.from_np(destination), orientation)

    def exec(self):
        """
        Exécute le déplacement
        """
        self.player.ai_command = AICommand(self.player, AICommandType.MOVE,
                                           **{"pose_goal": self.generate_destination()})
        return self.player.ai_command
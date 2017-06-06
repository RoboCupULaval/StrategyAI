# Under MIT license, see LICENSE.txt
import numpy as np
from RULEngine.Util.Pose import Pose
from .Action import Action
# from ...Util.types import AICommand
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType


class RotateAround(Action):
    """

    """
    def __init__(self, p_game_state, p_player_id, target, rayon):
        """
            :param p_game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui se déplace
            :param target: Pose du centre de rotation
            :param rayon: Distance entre le centre du robot et le centre de rotation
        """
        Action.__init__(self, p_game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        self.player_id = p_player_id
        self.target = target
        self.game_state = p_game_state
        self.rayon = rayon

    def generate_destination(self):
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
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
        destination = self.generate_destination()
        return AICommand(self.player_id, AICommandType.MOVE, **{"pose_goal": destination})
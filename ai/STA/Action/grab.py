# Under MIT license, see LICENSE.txt
import numpy as np
from .Action import Action
# from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType


class Grab(Action):
    """
    Action Move_to: Deplace le robot en vitesse
    Methodes :
        exec(self): Retourne la vitesse en pose
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        speed_pose : Pose representant le vecteur vitesse x,y et la vitesse en orientation du robot
    """
    def __init__(self, p_game_state, p_player_id):
        """
            :param p_game_state: L'etat courant du jeu.
            :param p_player_id: Identifiant du joueur qui se deplace
            :param p_destination: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, p_game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        self.player_id = p_player_id
        self.speed_pose = Pose()

    def exec(self):
        """
        Execute le deplacement
        :return: Un tuple (Pose, kick)
                     ou Pose est la destination du joueur
                        kick est faux (on ne botte pas)
        """
        ball = self.game_state.get_ball_position().conv_2_np()
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        player_to_ball = ball - player
        player_to_ball = 0.3 * player_to_ball / np.linalg.norm(player_to_ball)
        self.speed_pose = Pose(Position.from_np(player_to_ball))
        return AICommand(self.player_id, AICommandType.MOVE,
                         **{"pose_goal": self.speed_pose, "speed_flag": True})

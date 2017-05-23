# Under MIT license, see LICENSE.txt
from .Action import Action
# from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType


class Move(Action):
    """
    Action Move_to: Deplace le robot en vitesse
    Methodes :
        exec(self): Retourne la vitesse en pose
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        speed_pose : Pose representant le vecteur vitesse x,y et la vitesse en orientation du robot
    """
    def __init__(self, game_state, p_player_id, p_speed_pose):
        """
            :param game_state: L'etat courant du jeu.
            :param p_player_id: Identifiant du joueur qui se deplace
            :param p_destination: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert(isinstance(p_speed_pose, Pose))
        self.player_id = p_player_id
        self.speed_pose = p_speed_pose

    def exec(self):
        """
        Execute le deplacement
        :return: Un tuple (Pose, kick)
                     ou Pose est la destination du joueur
                        kick est faux (on ne botte pas)
        """

        return AICommand(self.player_id, AICommandType.MOVE,
                         **{"pose_goal": self.speed_pose, "speed_flag": True})

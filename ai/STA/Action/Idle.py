# Under MIT license, see LICENSE.txt
from .Action import Action
from ...Util.types import AICommand
from RULEngine.Util.constant import PLAYER_PER_TEAM


class Idle(Action):
    """
    Action Stop: Arrête le robot
    Méthodes :
        exec(self): Retourne la position du joueur qui l'a appelé
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    """
    def __init__(self, p_info_manager, p_player_id):
        """
            :param p_info_manager: référence vers l'InfoManager
            :param p_player_id: Identifiant du joueur qui s'arrête
        """
        Action.__init__(self, p_info_manager)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        self.player_id = p_player_id

    def exec(self):
        """
        Exécute l'arrêt
        :return: Un tuple (Pose, kick) où Pose est la position du joueur et kick est nul (on ne botte pas)
        """
        move_destination = self.info_manager.get_player_pose(self.player_id)
        kick_strength = 0
        return AICommand(move_destination, kick_strength)

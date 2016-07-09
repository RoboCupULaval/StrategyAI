# Under MIT license, see LICENSE.txt
from .Action import Action
from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose


class MoveTo(Action):
    """
    Action Move_to: Déplace le robot
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        destination : La destination (pose) que le joueur doit atteindre
    """
    def __init__(self, p_info_manager, p_player_id, p_destination):
        """
            :param p_info_manager: référence vers l'InfoManager
            :param p_player_id: Identifiant du joueur qui se déplace
            :param p_destination: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, p_info_manager)
        assert(isinstance(p_player_id, int))
        assert(isinstance(p_destination, Pose))
        self.player_id = p_player_id
        self.destination = p_destination

    def exec(self):
        """
        Exécute le déplacement
        :return: Un tuple (Pose, kick)
                     où Pose est la destination du joueur
                        kick est faux (on ne botte pas)
        """
        move_destination = self.destination
        kick_strength = 0
        return AICommand(move_destination, kick_strength)

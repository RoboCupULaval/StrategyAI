# Under MIT license, see LICENSE.txt
from .Action import Action
from ...Util.types import AICommand

class Move_to(Action):
    '''
    Action Move_to: Déplace le robot
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    '''
    def __init__(self, p_info_manager, p_player_id, p_destination):
        """
            :param pInfoManager: référence vers l'InfoManager
            :param pPlayerId: Identifiant du joueur qui s'arrête
            :param pDestination: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, p_info_manager)
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

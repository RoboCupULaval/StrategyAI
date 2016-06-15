from . import Action

class Stop(Action):
    '''
    Action Stop: Arrête le robot
    Méthodes :
        exec(self): Retourne la position du joueur qui l'a appelé
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    '''
    def __init__(self, pInfoManager, pPlayerId):
        """
        Initialise l'action Stop
        :param pInfoManager: référence vers l'InfoManager
        :param pPlayerId: Identifiant du joueur qui s'arrête
        """
        Action.__init__(self, pInfoManager)
        # Note: Non sécuritaire, car on pourrait mettre la position d'un joueur adverse
        self.PlayerId = pPlayerId

    def exec(self):
        """
        Exécute l'arrêt
        :return: Un tuple (Pose, kick)
                     où Pose est la position du joueur
                        kick est faux (on ne botte pas)
        """
        pose = self.InfoManager.get_player_position(self.PlayerId)
        kick = False
        return tuple(pose, kick)

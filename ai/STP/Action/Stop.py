from . import Action

class Stop(Action):
    '''
    Action Stop: Arrête le robot
    Méthodes :
        exec(self): Retourne la position du joueur qui l'a appelé
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    '''
    def __init__(self, info_manager, player_id):
        Action.__init__(self, info_manager)
        # Note: Non sécuritaire, car on pourrait mettre la position d'un joueur adverse
        self.player_id = player_id

    def exec(self):
        pose = self.info_manager.get_player_position(self.player_id)
        kick = False
        return tuple(pose, kick)

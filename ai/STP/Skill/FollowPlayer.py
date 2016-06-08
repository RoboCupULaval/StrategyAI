from . import Action

class FollowPlayer(Action):
    """
    Action FollowPlayer: Fait en sorte que le robot suive un autre robot
    Méthodes :
        exec(self): Retourne la position du joueur à suivre
    Attributs (en plus de ceux de Action):
        target_id : L'identifiant du joueur à suivre
    """
    def __init__(self, info_manager, target_id):
        Action.__init__(self, info_manager);
        self.target_id = target_id

    def exec(self):
        pose = self.info_manager.get_player_position(self.target_id)
        kick = False
        return tuple(pose, kick)
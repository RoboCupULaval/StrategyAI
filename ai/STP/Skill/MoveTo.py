from . import Action

class MoveTo(Action):
    """
    Action Move: Fait en sorte que le robot suive un autre robot
    Méthodes :
        exec(self): Retourne la position du joueur à suivre
    Attributs (en plus de ceux de Action):
        target_id : L'identifiant du joueur à suivre
    """
    def __init__(self, info_manager, target):
        Action.__init__(self, info_manager)
        self.target = target;
        self.kick = False

    def exec(self):
        return tuple(self.target, self.kick)

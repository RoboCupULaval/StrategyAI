# Under MIT license, see LICENSE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from ai.states.game_state import GameState
from .Action import Action
from ai.Util.ai_command import AICommand, AICommandType


class Idle(Action):
    """
    Action Stop: Arrête le robot
    Méthodes :
        exec(self): Retourne la position du joueur qui l'a appelé
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    """
    def __init__(self, game_state: GameState, player: OurPlayer):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui s'arrête
        """
        Action.__init__(self, game_state, player)

    def exec(self):
        """
        Exécute l'arrêt
        :return: Un tuple (None, kick) où None pour activer une commande de stop et kick est nul (on ne botte pas)
        """
        # un None pour que le coachcommandsender envoi une command vide.
        self.player.ai_command = AICommand(self.player, AICommandType.STOP)
        return self.player.ai_command

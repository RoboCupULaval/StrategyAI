# Under MIT license, see LICENSE.txt
from RULEngine.GameDomainObjects.OurPlayer import OurPlayer
from ai.states.game_state import GameState
from .Action import Action
from ai.Util.ai_command import AICommand, AICommandType, AIControlLoopType
from RULEngine.Util.SpeedPose import SpeedPose

class Idle(Action):
    """
    Action Stop: Arrête le robot
    Méthodes :
        exec(self): Retourne une ai_command STOP
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
        """
        return AICommand(self.player,
                         AICommandType.STOP)

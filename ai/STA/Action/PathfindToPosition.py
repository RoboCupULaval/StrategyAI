# Under MIT license, see LICENSE.txt
from Util.ai_command import CmdBuilder
from ai.GameDomainObjects import Player
from Util import Pose

from ai.STA.Action import Action
from ai.states.game_state import GameState


class PathfindToPosition(Action):
    """
    Action Move_to: Déplace le robot avec flag pathfinder
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        destination : La destination (pose) que le joueur doit atteindre
    """
    def __init__(self, game_state: GameState, player: Player, p_destination: Pose, cruise_speed: [int, float]=0.2):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui se déplace
            :param p_destination: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, game_state, player)
        assert isinstance(p_destination, Pose)
        self.destination = p_destination
        self.cruise_speed = cruise_speed

    def exec(self):
        """
        Exécute le déplacement
        :return: Un tuple (Pose, kick)
                     où Pose est la destination du joueur
                        kick est faux (on ne botte pas)
        """
        return CmdBuilder().addMoveTo(self.destination, cruise_speed=self.cruise_speed).build()

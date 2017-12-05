# Under MIT license, see LICENSE.txt
from RULEngine.GameDomainObjects.player import Player
from RULEngine.Util.Pose import Pose
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

# TODO remove this and use MoveToPosition (Simon B)


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
        return AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.destination,
                                                             "pathfinder_on": True,
                                                             "cruise_speed": self.cruise_speed})

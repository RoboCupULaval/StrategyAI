# Under MIT license, see LICENSE.txt
from RULEngine.Game.Player import Player
from ai.states.game_state import GameState
from .Action import Action
# from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType


class PathfindToPosition(Action):
    """
    Action Move_to: Déplace le robot
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        destination : La destination (pose) que le joueur doit atteindre
    """
    def __init__(self, game_state: GameState, player: Player, p_destination, cruise_speed=0.2):
        """
            :param game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui se déplace
            :param p_destination: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, game_state)
        assert(isinstance(player, Player))
        assert(isinstance(p_destination, Pose))
        self.player_id = player.id
        self.destination = p_destination
        self.cruise_speed = cruise_speed

    def exec(self):
        """
        Exécute le déplacement
        :return: Un tuple (Pose, kick)
                     où Pose est la destination du joueur
                        kick est faux (on ne botte pas)
        """
        move_destination = self.destination
        return AICommand(self.player_id,
                         AICommandType.MOVE,
                         **{"pose_goal": move_destination,
                            "pathfinder_on": True,
                            "cruise_speed": self.cruise_speed})

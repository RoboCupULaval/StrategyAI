# Under MIT license, see LICENSE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.game_state import GameState


class MoveToPosition(Action):
    """
    Action Move_to: Déplace le robot
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        destination : La destination (pose) que le joueur doit atteindre
    """
    def __init__(self, game_state: GameState, player: OurPlayer, p_destination: Pose, pathfinder_on=True, cruise_speed: [int, float]=1):
        """
            :param game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui se déplace
            :param p_destination: destination (pose) que le joueur doit atteindre
            :param pathfinder_on:
            :param cruise_speed
        """
        Action.__init__(self, game_state, player)
        assert isinstance(p_destination, Pose)
        assert isinstance(cruise_speed, (int, float))
        self.destination = p_destination
        self.pathfinder_on = pathfinder_on
        self.cruise_speed = cruise_speed

    def exec(self):
        """
        Exécute le déplacement
        :return:
        """
        return AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.destination,
                                                             "pathfinder_on": self.pathfinder_on,
                                                             "cruise_speed": self.cruise_speed})

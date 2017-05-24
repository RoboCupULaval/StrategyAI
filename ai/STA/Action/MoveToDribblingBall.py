# Under MIT licence, see LICENCE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_angle
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.game_state import GameState

__author__ = 'Robocup ULaval'


class MoveToDribblingBall(Action):
    """
    Action MoveWithBall: Déplace le robot en tenant compte de la possession de la balle
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        destination : La position où on souhaite déplacer le robot
    """
    def __init__(self, game_state: GameState, player: OurPlayer, p_destination: Position):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui se déplace avec la balle
            :param p_destination: La position où on souhaite déplacer le robot
        """
        Action.__init__(self, game_state, player)
        assert(isinstance(p_destination, Position))
        self.destination = p_destination

    def exec(self):
        """
        Exécute le déplacement en tenant compte de la possession de la balle. Le robot se déplace vers la destination,
        mais s'oriente de façon à garder la balle sur le dribleur. C'est la responsabilité de la Tactique de faire les
        corrections de trajectoire nécessaire.
        :return:
        """
        # TODO: Améliorer le comportement en ajoutant l'intervalle d'anle correspondant à la largeur du dribbleur
        destination_orientation = get_angle(self.player.pose.position,
                                            self.game_state.get_ball_position())
        destination_pose = Pose(self.destination, destination_orientation)
        self.player.ai_command = AICommand(self.player, AICommandType.MOVE, **{"pose_goal": destination_pose})
        return self.player.ai_command

# Under MIT licence, see LICENCE.txt
from .Action import Action
from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Util.geometry import get_angle
from RULEngine.Util.constant import PLAYER_PER_TEAM

__author__ = 'Robocup ULaval'


class MoveWithBall(Action):
    """
    Action MoveWithBall: Déplace le robot en tenant compte de la possession de la balle
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        destination : La position où on souhaite déplacer le robot
    """
    def __init__(self, p_game_state, p_player_id, p_destination):
        """
            :param p_info_manager: référence vers l'InfoManager
            :param p_player_id: Identifiant du joueur qui se déplace avec la balle
            :param p_destination: La position où on souhaite déplacer le robot
        """
        Action.__init__(self, p_game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert(isinstance(p_destination, Position))
        self.player_id = p_player_id
        self.destination = p_destination

    def exec(self):
        """
        Exécute le déplacement en tenant compte de la possession de la balle. Le robot se déplace vers la destination,
        mais s'oriente de façon à garder la balle sur le dribleur. C'est la responsabilité de la Tactique de faire les
        corrections de trajectoire nécessaire.
        :return: Un tuple (Pose, kick) où Pose est la destination du joueur kick est faux (on ne botte pas)
        """
        # TODO: Améliorer le comportement en ajoutant l'intervalle d'anle correspondant à la largeur du dribleur
        destination_orientation = get_angle(self.game_state.get_player_pose(self.player_id).position,
                                            self.game_state.get_ball_position())
        destination_pose = Pose(self.destination, destination_orientation)
        kick_strength = 0
        return AICommand(destination_pose, kick_strength)

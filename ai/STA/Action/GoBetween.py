# Under MIT licence, see LICENCE.txt
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

__author__ = 'Robocup ULaval'


class GoBetween(Action):
    """
    Action GoBetween: Déplace le robot au point le plus proche sur la droite entre deux positions passées en paramètres
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        position1 : La première position formant la droite
        position2 : La deuxième position formant la droite
        target : La position vers laquelle le robot devrait s'orienter
        minimum_distance : La distance minimale qu'il doit y avoir entre le robot et chacun des points
    """
    def __init__(self, game_state: GameState, player: OurPlayer, position1: Position, position2: Position,
                 target: Position, p_minimum_distance: [int, float]=0):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui doit se déplacer
            :param position1: La première position formant la droite
            :param position2: La deuxième position formant la droite
            :param target: La position vers laquelle le robot devrait s'orienter
            :param p_minimum_distance: La distance minimale qu'il doit y avoir entre le robot et chacun des points
        """
        Action.__init__(self, game_state, player)
        assert(isinstance(position1, Position))
        assert(isinstance(position2, Position))
        assert(isinstance(target, Position))
        assert(isinstance(p_minimum_distance, (int, float)))
        self.position1 = position1
        self.position2 = position2
        self.target = target
        self.minimum_distance = p_minimum_distance
        self.pathfind = True

    def get_destination(self) -> Pose:
        """
        Calcul le point le plus proche du robot sur la droite entre les deux positions
        :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
        """
        pt1 = self.position1
        pt2 = self.position2
        target = self.target

        delta = self.minimum_distance * ((pt2 - pt1).normalized())
        pt1 = pt1 + delta
        pt2 = pt2 - delta

        pt1_to_target = target - pt1
        pt2_to_target = target - pt2
        pt1_to_pt2 = pt2 - pt1
        proj_pt1_to_pt2 = pt1_to_target[0] * pt1_to_pt2[0] + pt1_to_target[1] * pt1_to_pt2[1]

        pt1_to_pt2_mag = pt1_to_pt2[0] ** 2 + pt1_to_pt2[1] ** 2
        proj_mag = proj_pt1_to_pt2 / pt1_to_pt2_mag
        destination = pt1 + Position(pt1_to_pt2[0] * proj_mag, pt1_to_pt2[1] * proj_mag)

        # This handle the case where the projection is not between the two points
        outside_x = (destination[0] > pt1[0] and destination[0] > pt2[0]) or \
                    (destination[0] < pt1[0] and destination[0] < pt2[0])
        outside_y = (destination[1] > pt1[1] and destination[1] > pt2[1]) or \
                    (destination[1] < pt1[1] and destination[1] < pt2[1])
        if outside_x or outside_y:
            if pt1_to_target.norm() < pt2_to_target.norm():
                destination = pt1
            else:
                destination = pt2

        destination_orientation = (target - destination).angle()

        return Pose(destination, destination_orientation)

    def exec(self):
        return AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.get_destination(),
                                                             "pathfinder_on": self.pathfind})

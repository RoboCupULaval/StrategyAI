# Under MIT licence, see LICENCE.txt
import math
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
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
        player = self.player.pose.position.conv_2_np()
        pt1 = self.position1.conv_2_np()
        pt2 = self.position2.conv_2_np()
        delta = self.minimum_distance * (pt2 - pt1) / np.linalg.norm(pt2 - pt1)
        pt1 = pt1 + delta
        pt2 = pt2 - delta

        pt1_to_player = player - pt1
        pt2_to_player = player - pt2
        pt1_to_pt2 = pt2 - pt1

        destination = np.cross(pt1_to_player, pt1_to_pt2) / np.linalg.norm(pt1_to_pt2) + player
        outside_x = (destination[0] > pt1[0] and destination[0] > pt2[0]) or \
                    (destination[0] < pt1[0] and destination[0] < pt2[0])
        outside_y = (destination[1] > pt1[1] and destination[1] > pt2[1]) or \
                    (destination[1] < pt1[1] and destination[1] < pt2[1])
        if outside_x or outside_y:
            if np.linalg.norm(pt1_to_player) > np.linalg.norm(pt2_to_player):
                destination = pt1
            else:
                destination = pt2
        target = self.target.conv_2_np()
        player_to_target = target - player
        destination_orientation = np.arctan2(player_to_target[1], player_to_target[0])

        '''
        delta_x = self.position2.x - self.position1.x
        delta_y = self.position2.y - self.position1.y

        if delta_x != 0 and delta_y != 0:   # droite quelconque
            # Équation de la droite reliant les deux positions
            a1 = delta_y / delta_x                                  # pente
            b1 = self.position1.y - a1*self.position1.x             # ordonnée à l'origine

            # Équation de la droite perpendiculaire
            a2 = -1/a1                                              # pente perpendiculaire à a1
            b2 = robot_position.y - a2*robot_position.x             # ordonnée à l'origine

            # Calcul des coordonnées de la destination
            x = (b2 - b1)/(a1 - a2)                                 # a1*x + b1 = a2*x + b2
            y = a1*x + b1
        elif delta_x == 0:  # droite verticale
            x = self.position1.x
            y = robot_position.y
        elif delta_y == 0: # droite horizontale
            x = robot_position.x
            y = self.position1.y

        destination_position = Position(x, y)

        # Vérification que destination_position se trouve entre position1 et position2
        distance_positions = math.sqrt(delta_x**2 + delta_y**2)
        distance_dest_pos1 = get_distance(self.position1, destination_position)
        distance_dest_pos2 = get_distance(self.position2, destination_position)

        if distance_dest_pos1 >= distance_positions and distance_dest_pos1 > distance_dest_pos2:
            # Si position2 est entre position1 et destination_position
            new_x = self.position2.x - self.minimum_distance * delta_x / distance_positions
            new_y = self.position2.y - self.minimum_distance * delta_y / distance_positions
            destination_position = Position(new_x, new_y)
        elif distance_dest_pos2 >= distance_positions and distance_dest_pos2 > distance_dest_pos1:
            # Si position1 est entre position2 et destination_position
            new_x = self.position1.x + self.minimum_distance * delta_x / distance_positions
            new_y = self.position1.y + self.minimum_distance * delta_y / distance_positions
            destination_position = Position(new_x, new_y)

        # Vérification que destination_position respecte la distance minimale
        if distance_dest_pos1 <= distance_dest_pos2:
            destination_position = stayOutsideCircle(destination_position, self.position1, self.minimum_distance)
        else:
            destination_position = stayOutsideCircle(destination_position, self.position2, self.minimum_distance)

        # Calcul de l'orientation de la pose de destination
        destination_orientation = get_angle(destination_position, self.target)

        destination_pose = {"pose_goal": Pose(destination_position, destination_orientation)}
        kick_strength = 0
        '''
        return Pose(Position.from_np(destination), destination_orientation)

    def exec(self):
        destination_pose = {"pose_goal": self.get_destination(), "pathfinder_on": self.pathfind}
        self.player.ai_command = AICommand(self.player, AICommandType.MOVE, **destination_pose)
        return self.player.ai_command

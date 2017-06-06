# Under MIT licence, see LICENCE.txt
import math as m
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.geometry import rotate_point_around_origin, get_angle, get_distance
from RULEngine.Util.constant import ANGLE_TO_HALT, POSITION_DEADZONE
from RULEngine.Util.Pose import Pose
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'


class RotateAround(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: état courant du jeu
        player: Instance du joueur auquel est assigné la tactique
        center_position : Position autour de laquelle le robot doit effectuer une révolution
        target : Position à laquelle le robot doit faire face à la fin de sa révolution
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
    """

    def __init__(self, game_state: GameState, player: OurPlayer, center_position, target: Pose, args: List[str]=None):
        Tactic.__init__(self, game_state, player, target, args)
        self.ANGLE_INCREMENT = m.pi/8
        self.pose_list = []
        self.index = 0
        self.origin = center_position
        self.initial_position = None
        self.initial_orientation = None
        self.initial_distance = None
        self.initial_angle = None
        self.target_angle = None
        self.delta_angle = None
        self.num_points = None
        self.angle_increment = None

        self.status_flag = Flags.INIT
        self.current_state = self.calculate_path
        self.next_state = self.rotate_around

    def rotate_around(self):
        if self._has_reached_pose(self.pose_list[self.index]):
            self.index += 1
            if self.index == len(self.pose_list):   # position finale atteinte
                self.status_flag = Flags.SUCCESS
                self.next_state = self.halt
                action = Idle(self.game_state, self.player)
            else:                                   # position intermédiaire atteinte
                self.status_flag = Flags.WIP
                action = MoveToPosition(self.game_state, self.player, self.pose_list[self.index])
        else:
            self.status_flag = Flags.WIP
            action = MoveToPosition(self.game_state, self.player, self.pose_list[self.index])
        return action

    def calculate_path(self):
        self.initial_position = self.player.pose.position
        self.initial_orientation = self.player.pose.orientation
        self.initial_distance = get_distance(self.origin, self.initial_position)
        self.initial_angle = get_angle(self.origin, self.initial_position)
        self.target_angle = get_angle(self.origin, self.target.position)
        self.delta_angle = (self.target_angle + m.pi - self.initial_angle) % (2 * m.pi)
        if self.delta_angle > m.pi:
            self.delta_angle -= 2 * m.pi

        if m.fabs(self.delta_angle) >= self.ANGLE_INCREMENT:
            self.num_points = int(
                m.fabs(self.delta_angle) // self.ANGLE_INCREMENT)  # incrément d'environ pi/8 radians (22.5 degrés)
            self.angle_increment = self.delta_angle / self.num_points
        else:
            self.num_points = 1
            self.angle_increment = self.delta_angle

        for i in range(self.num_points):
            pos = rotate_point_around_origin(self.initial_position, self.origin, (i + 1) * self.angle_increment)
            theta = self.initial_orientation + (i + 1) * self.angle_increment
            self.pose_list.append(Pose(pos, theta))

        self.next_state = self.rotate_around
        return MoveToPosition(self.game_state, self.player, self.pose_list[self.index])

    def _has_reached_pose(self, pose):
        same_position = get_distance(self.player.pose.position, pose.position) <= POSITION_DEADZONE
        same_orientation = m.fabs(self.player.pose.orientation - pose.orientation) <= ANGLE_TO_HALT
        return same_position and same_orientation

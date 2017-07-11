# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS, POSITION_DEADZONE, ANGLE_TO_HALT
from ai.Algorithm.evaluation_module import best_position_in_region
from ai.STA.Action.AllStar import AllStar
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.Util.ai_command import AICommandType
from ai.states.game_state import GameState
import random

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class GoToRandomPosition(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player: Instance du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, game_state: GameState, player: OurPlayer, center_of_zone: Position, height_of_zone,
                 width_of_zone, args: List[str]=None,
                 auto_position=False):
        Tactic.__init__(self, game_state, player, args=args)
        self.current_state = self.exec
        self.next_state = self.exec
        self.auto_position = auto_position
        self.center_of_zone = center_of_zone
        self.height_of_zone = height_of_zone
        self.width_of_zone = width_of_zone
        self.bottom_left_corner = Position(self.center_of_zone[0] - self.width_of_zone / 2,
                                           self.center_of_zone[1] - self.height_of_zone / 2)
        self.grid_of_positions = []
        self.discretisation = 100
        for i in range(int(self.width_of_zone / self.discretisation)):
            for j in range(int(self.height_of_zone / self.discretisation)):
                self.grid_of_positions.append(self.bottom_left_corner + Position(self.discretisation * i,
                                                                                 self.discretisation * j))
        self.current_position_index_to_go = random.randint(0, len(self.grid_of_positions))
        self.current_position_to_go = self.grid_of_positions[self.current_position_index_to_go]
        self.current_angle_to_go = random.randint(0, 100) * np.pi / 100.
        self.next_pose = Pose(self.current_position_to_go, self.current_angle_to_go)

    def exec(self):

        if self.check_success():
            self.current_position_index_to_go = random.randint(0, len(self.grid_of_positions))
            self.current_position_to_go = self.grid_of_positions[self.current_position_index_to_go]
            self.current_angle_to_go = random.randint(0, 100) * np.pi / 100.
            self.next_pose = Pose(self.current_position_to_go, self.current_angle_to_go)
        self.next_state = self.exec

        return GoToPositionPathfinder(self.game_state, self.player, self.next_pose).exec()

    def check_success(self):
        distance = (self.player.pose - self.next_pose).position.norm()
        if distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.next_pose, abs_tol=ANGLE_TO_HALT):
            return True
        return False


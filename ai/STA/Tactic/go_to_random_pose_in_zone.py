# Under MIT licence, see LICENCE.txt
import random
from typing import List

import numpy as np
from Util.Pose import Pose, Position

from RULEngine.GameDomainObjects.player import Player
from Util.constant import BALL_RADIUS, ROBOT_RADIUS, POSITION_DEADZONE, ANGLE_TO_HALT

from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class GoToRandomPosition(Tactic):
    def __init__(self, game_state: GameState, player: Player, center_of_zone: Position, height_of_zone,
                 width_of_zone, args: List[str]=None):
        super().__init__(game_state, player, args=args)
        self.current_state = self.exec
        self.next_state = self.exec
        self.center_of_zone = center_of_zone
        self.height_of_zone = height_of_zone
        self.width_of_zone = width_of_zone
        self.bottom_left_corner = Position(self.center_of_zone[0] - self.width_of_zone / 2,
                                           self.center_of_zone[1] - self.height_of_zone / 2)
        self.grid_of_positions = []
        discretisation = 100
        for i in range(int(self.width_of_zone / discretisation)):
            for j in range(int(self.height_of_zone / discretisation)):
                self.grid_of_positions.append(self.bottom_left_corner + Position(discretisation * i,
                                                                                 discretisation * j))
        self.current_position_index_to_go = random.randint(0, len(self.grid_of_positions) - 1)
        self.current_position_to_go = self.grid_of_positions[self.current_position_index_to_go]
        self.current_angle_to_go = random.randint(0, 100) * np.pi / 100.
        self.next_pose = Pose(self.current_position_to_go, self.current_angle_to_go)

    def exec(self):

        if self.check_success():
            self.current_position_index_to_go = random.randint(0, len(self.grid_of_positions) - 1)
            self.current_position_to_go = self.grid_of_positions[self.current_position_index_to_go]
            self.current_angle_to_go = random.randint(-100, 100) * np.pi / 100.
            self.next_pose = Pose(self.current_position_to_go, self.current_angle_to_go)
        self.next_state = self.exec

        return GoToPositionPathfinder(self.game_state, self.player, self.next_pose).exec()

    def check_success(self):
        distance = (self.player.pose - self.next_pose).position.norm()
        if distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.next_pose, abs_tol=ANGLE_TO_HALT):
            return True
        return False

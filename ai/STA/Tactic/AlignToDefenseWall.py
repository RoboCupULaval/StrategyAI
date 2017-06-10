# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.STA.Tactic.Tactic import Tactic
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.0


class AllignToDefenseWall(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, number_of_robots: int=0, robot_formation_number: int=0,
                 args: List[str]=None):
        Tactic.__init__(self, game_state, player, args=args)
        self.current_state = self.go_allign
        self.next_state = self.go_allign
        self.last_time = time.time()
        self.number_of_robots = number_of_robots
        self.robot_formation_number = robot_formation_number

    def go_allign(self):
        #dodo time
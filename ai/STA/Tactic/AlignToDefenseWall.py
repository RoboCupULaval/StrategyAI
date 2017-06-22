# Under MIT licence, see LICENCE.txt

import numpy as np

from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.STA.Tactic.Tactic import Tactic


__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.0


class GoKick(Tactic):
    def __init__(self):
        self.player = None

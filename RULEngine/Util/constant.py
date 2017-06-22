# Under MIT License, see LICENSE.txt
""" Module définissant des constantes de programmations python pour l'IA """

from enum import Enum

__author__ = 'RoboCupULaval'

ROBOT_RADIUS = 90
BALL_RADIUS = 21
PLAYER_PER_TEAM = 12

# Communication information
DEBUG_RECEIVE_BUFFER_SIZE = 100

# Deadzones
SPEED_DEAD_ZONE_DISTANCE = 150
#POSITION_DEADZONE = SPEED_DEAD_ZONE_DISTANCE+50

# Radius and angles for tactics
DISTANCE_BEHIND = ROBOT_RADIUS + 30  # in millimeters
ANGLE_TO_GRAB_BALL = 1  # in radians; must be large in case ball moves fast
RADIUS_TO_GRAB_BALL = ROBOT_RADIUS + 30
ANGLE_TO_HALT = 0.05  # 3 degrees
RADIUS_TO_HALT = ROBOT_RADIUS + BALL_RADIUS

# Deadzones
POSITION_DEADZONE = ROBOT_RADIUS * 0.5

# Orientation abs_tol
ORIENTATION_ABSOLUTE_TOLERANCE = 0.01  # 0.5 degree


# TeamColor
class TeamColor(Enum):
    def __str__(self):
        return 'blue' if self == TeamColor.BLUE else 'yellow'
    YELLOW = 0
    BLUE = 1


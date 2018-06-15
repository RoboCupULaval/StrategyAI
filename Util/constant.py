# Under MIT License, see LICENSE.txt
""" Module définissant des constantes de programmations python pour l'IA """

from enum import Enum


ROBOT_RADIUS = 90
ROBOT_DIAMETER = ROBOT_RADIUS * 2
ROBOT_CENTER_TO_KICKER = 50
BALL_RADIUS = 21
PLAYER_PER_TEAM = 12
MAX_PLAYER_ON_FIELD_PER_TEAM = 6
BALL_OUTSIDE_FIELD_BUFFER = 200

# Radius and angles for tactics
DISTANCE_BEHIND = ROBOT_RADIUS + 30  # in millimeters
ANGLE_TO_GRAB_BALL = 1  # in radians; must be large in case ball moves fast
RADIUS_TO_GRAB_BALL = ROBOT_RADIUS + 30
ANGLE_TO_HALT = 0.05  # 3 degrees
RADIUS_TO_HALT = ROBOT_RADIUS + BALL_RADIUS

REASONABLE_OFFSET = 50  # To take into account the camera precision and other things
# Rules
KEEPOUT_DISTANCE_FROM_BALL = 500 + ROBOT_RADIUS + REASONABLE_OFFSET
KEEPOUT_DISTANCE_FROM_GOAL = ROBOT_RADIUS + REASONABLE_OFFSET

# Rule 9.4
INDIRECT_KICK_OFFSET = 200

# Deadzones
POSITION_DEADZONE = ROBOT_RADIUS * 0.1

# Orientation abs_tol
ORIENTATION_ABSOLUTE_TOLERANCE = 0.01  # 0.5 degree


# TeamColor
class TeamColor(Enum):

    def __str__(self):
        return 'blue' if self == TeamColor.BLUE else 'yellow'
    YELLOW = 0
    BLUE = 1

    
class KickForce(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    
class KickType(Enum):
    DIRECT = 0
    CHIP = 1


class DribbleState(Enum):
    AUTOMATIC = 0
    FORCE_STOP = 1
    FORCE_SPIN = 2

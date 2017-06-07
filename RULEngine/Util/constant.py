# Under MIT License, see LICENSE.txt
""" Module définissant des constantes de programmations python pour l'IA """
from .Position import Position
from .Pose import Pose
from enum import Enum

__author__ = 'RoboCupULaval'

ROBOT_RADIUS = 90
BALL_RADIUS = 22
PLAYER_PER_TEAM = 11
KICK_MAX_SPD = 8.0

# Field Parameters
FIELD_Y_TOP = 1090
FIELD_Y_BOTTOM = -1090
FIELD_X_LEFT = -1636
FIELD_X_RIGHT = 1636
FIELD_GOAL_RADIUS = 363
FIELD_GOAL_SEGMENT = 181

# Goal Parameters
FIELD_GOAL_Y_TOP = FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
FIELD_GOAL_Y_BOTTOM = (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
FIELD_GOAL_BLUE_X_LEFT = FIELD_X_LEFT
FIELD_GOAL_BLUE_X_RIGHT = FIELD_X_LEFT + FIELD_GOAL_RADIUS
FIELD_GOAL_YELLOW_X_LEFT = FIELD_X_RIGHT - FIELD_GOAL_RADIUS
FIELD_GOAL_YELLOW_X_RIGHT = FIELD_X_RIGHT

# Field Positions
FIELD_GOAL_BLUE_TOP_CIRCLE = Position(FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
FIELD_GOAL_BLUE_BOTTOM_CIRCLE = Position(FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
FIELD_GOAL_YELLOW_TOP_CIRCLE = Position(FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
FIELD_GOAL_YELLOW_BOTTOM_CIRCLE = Position(FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)

# Legal field dimensions
LEGAL_Y_TOP = 3000
# LEGAL_Y_TOP = 0
LEGAL_Y_BOTTOM = -3000
LEGAL_X_LEFT = -4500
LEGAL_X_RIGHT = 4500
# LEGAL_X_RIGHT = 0

# Simulation param
DELTA_T = 17 #ms, hack, à éviter

# Communication information
DEBUG_RECEIVE_BUFFER_SIZE = 100

# Deadzones
SPEED_DEAD_ZONE_DISTANCE = 150
#POSITION_DEADZONE = SPEED_DEAD_ZONE_DISTANCE+50

# Radius and angles for tactics
DISTANCE_BEHIND = ROBOT_RADIUS + 30  # in millimeters
ANGLE_TO_GRAB_BALL = 1  # in radians; must be large in case ball moves fast
RADIUS_TO_GRAB_BALL = ROBOT_RADIUS + 30
ANGLE_TO_HALT = 0.03
RADIUS_TO_HALT = ROBOT_RADIUS + BALL_RADIUS

# Deadzones
POSITION_DEADZONE = ROBOT_RADIUS * 0.5

# Orientation abs_tol
ORIENTATION_ABSOLUTE_TOLERANCE = 1e-4
SPEED_ABSOLUTE_TOLERANCE = 1e-3

# Speed
DEFAULT_MAX_SPEED = 1
DEFAULT_MIN_SPEED = 0.65


# TeamColor
class TeamColor(Enum):
    YELLOW_TEAM = 0
    BLUE_TEAM = 1
    def __str__(self):
        return 'blue' if self == TeamColor.BLUE_TEAM else 'yellow'

# FIXME: hack pour limiter le terrain facilement
def is_legal_field_pose(pose):
    if isinstance(pose, Pose):
        legal_x = pose.position.x < LEGAL_X_RIGHT and pose.position.x > LEGAL_X_LEFT
        legal_y = pose.position.y < LEGAL_Y_TOP and pose.position.y > LEGAL_Y_BOTTOM
        return legal_x and legal_y
    else:
        return False

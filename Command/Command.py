import math
from ..Util.Pose import Pose, Position
from ..Game.Player import Player
from ..Game.Team import Team
from ..Util.area import *
from ..Util.geometry import *
from ..Util.constant import *


class _Command(object):
    def __init__(self, player, team):
        self.player = player
        self.dribble = True
        self.dribble_speed = 10
        self.kick = False
        self.kick_speed = 0
        self.is_speed_command = False
        self.pose = Pose()
        self.team = team


# class SetSpeed(_Command):
#     def __init__(self, player, team, pose):
#         # Parameters Assertion
#         assert(isinstance(player, Player))
#         assert(isinstance(team, Team))
#         assert(isinstance(pose, Pose))
#
#         super().__init__(player, team)
#         self.is_speed_command = True
#         pose.orientation = pose.orientation * 180 / math.pi
#         if m.sqrt(pose.position.x ** 2 + pose.position.y ** 2) <= KICK_MAX_SPD :
#             self.pose = pose
#         else:
#             agl = m.radians(theta(pose.position.x, pose.position.y))
#             dst = KICK_MAX_SPD
#             x = dst * m.cos(agl)
#             y = dst * m.sin(agl)
#             self.pose = Pose(Position(x, y), convertAngle180(pose.orientation))


class MoveTo(_Command):
    def __init__(self, player, team, position):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(position, Position))

        super().__init__(player, team)
        self.pose.position = stayInsideSquare(position,
                                              FIELD_Y_TOP,
                                              FIELD_Y_BOTTOM,
                                              FIELD_X_LEFT,
                                              FIELD_X_RIGHT)
        self.pose.orientation = cvt_angle_180(player.pose.orientation)


class Rotate(_Command):
    def __init__(self, player, team, orientation):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(orientation, (int, float)))

        super().__init__(player, team)
        self.pose.orientation = cvt_angle_180(orientation)
        self.pose.position = stayInsideSquare(player.pose.position,
                                              FIELD_Y_TOP,
                                              FIELD_Y_BOTTOM,
                                              FIELD_X_LEFT,
                                              FIELD_X_RIGHT)


class MoveToAndRotate(_Command):
    def __init__(self, player, team, pose):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(pose, Pose))

        super().__init__(player, team)
        position = stayInsideSquare(pose.position,
                                    FIELD_Y_TOP,
                                    FIELD_Y_BOTTOM,
                                    FIELD_X_LEFT,
                                    FIELD_X_RIGHT)
        self.pose = Pose(position, cvt_angle_180(pose.orientation))


class Kick(_Command):
    def __init__(self, player, team, kick_speed=5):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(kick_speed, (int, float)))
        assert(0 <= kick_speed <= 8)

        super().__init__(player, team)
        self.kick = True
        self.kick_speed = kick_speed
        self.is_speed_command = True
        self.pose = player.pose


class Stop(_Command):
    def __init__(self, player, team):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))

        super().__init__(player, team)
        self.is_speed_command = True
        self.pose = Pose()

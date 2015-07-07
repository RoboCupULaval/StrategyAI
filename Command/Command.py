from .. import rule
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

    def to_robot_command(self):
        robot_command = rule.RobotCommand()
        robot_command.is_team_yellow = self.team.is_team_yellow
        robot_command.dribble = self.dribble
        robot_command.dribble_speed = self.dribble_speed
        robot_command.kick = self.kick
        robot_command.kick_speed = self.kick_speed
        robot_command.robot_id = self.player.id
        robot_command.stop = self.is_speed_command
        robot_command.pose.coord.x = self.pose.position.x
        robot_command.pose.coord.y = self.pose.position.y
        robot_command.pose.orientation = self.pose.orientation * math.pi / 180

        return robot_command


class SetSpeed(_Command):
    def __init__(self, player, team, pose):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(pose, Pose))

        super().__init__(player, team)
        self.is_speed_command = True
        pose.orientation = pose.orientation * 180 / math.pi
        if m.sqrt(pose.position.x ** 2 + pose.position.y ** 2) <= KICK_MAX_SPD :
            self.pose = pose
        else:
            agl = m.radians(theta(pose.position.x, pose.position.y))
            dst = KICK_MAX_SPD
            x = dst * m.cos(agl)
            y = dst * m.sin(agl)
            self.pose = Pose(Position(x, y), convertAngle180(pose.orientation))


class MoveTo(_Command):
    def __init__(self, player, team, position):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(position, Position))

        super().__init__(player, team)
        self.pose.position = stayInsideSquare(position,
                                              FIELD_X_TOP,
                                              FIELD_X_BOTTOM,
                                              FIELD_Y_LEFT,
                                              FIELD_Y_RIGHT)
        self.pose.orientation = convertAngle180(player.pose.orientation)


class Rotate(_Command):
    def __init__(self, player, team, orientation):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(orientation, (int, float)))

        super().__init__(player, team)
        self.pose.orientation = convertAngle180(orientation)
        self.pose.position = stayInsideSquare(player.pose.position,
                                              FIELD_X_TOP,
                                              FIELD_X_BOTTOM,
                                              FIELD_Y_LEFT,
                                              FIELD_Y_RIGHT)


class MoveToAndRotate(_Command):
    def __init__(self, player, team, pose):
        # Parameters Assertion
        assert(isinstance(player, Player))
        assert(isinstance(team, Team))
        assert(isinstance(pose, Pose))

        super().__init__(player, team)
        self.pose = Pose(stayInsideSquare(pose.position,
                                          FIELD_X_TOP,
                                          FIELD_X_BOTTOM,
                                          FIELD_Y_LEFT,
                                          FIELD_Y_RIGHT),
                         convertAngle180(pose.orientation))


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

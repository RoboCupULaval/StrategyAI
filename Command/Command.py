from .. import rule
import math
from ..Util.Pose import Pose
from ..Util.constant import PLAYER_PER_TEAM


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
        robot_command.is_team_yellow = self.team
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
        super().__init__(player, team)
        self.is_speed_command = True
        pose.orientation = pose.orientation * 180 / math.pi
        self.pose = pose


class MoveTo(_Command):
    def __init__(self, player, team, position):
        super().__init__(player, team)
        self.pose.position = position
        self.pose.orientation = player.pose.orientation


class Rotate(_Command):
    def __init__(self, player, team, orientation):
        super().__init__(player, team)
        self.pose.orientation = orientation
        self.pose.position = player.pose.position


class MoveToAndRotate(_Command):
    def __init__(self, player, team, pose):
        super().__init__(player, team)
        self.pose = pose


class Kick(_Command):
    def __init__(self, player, team, kick_speed=5):
        super().__init__(player, team)
        self.kick = True
        self.kick_speed = kick_speed
        self.is_speed_command = True
        self.pose = player.pose


class Stop(_Command):
    def __init__(self, player, team):
        super().__init__(player, team)
        self.is_speed_command = True
        self.pose = Pose()

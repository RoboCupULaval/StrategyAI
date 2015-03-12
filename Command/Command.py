import rule
import math
from Util.Pose import Pose
from Util.constant import PLAYER_PER_TEAM


class _Command(object):
    def __init__(self, player):
        self.player = player
        self.dribble = False
        self.dribble_speed = 0
        self.kick = False
        self.kick_speed = 0
        self.is_speed_command = False
        self.pose = Pose()

    def to_robot_command(self):
        robot_command = rule.RobotCommand()
        player_id = self._get_player_id()
        robot_command.is_team_yellow = self._is_player_team_yellow()
        robot_command.dribble = self.dribble
        robot_command.dribble_speed = self.dribble_speed
        robot_command.kick = self.kick
        robot_command.kick_speed = self.kick_speed
        robot_command.robot_id = player_id
        robot_command.stop = self.is_speed_command
        robot_command.pose.coord.x = self.pose.position.x
        robot_command.pose.coord.y = self.pose.position.y
        robot_command.pose.orientation = self.pose.orientation * math.pi / 180

        return robot_command

    def _is_player_team_yellow(self):
        return self.player.id >= PLAYER_PER_TEAM

    def _get_player_id(self):
        player_id = self.player.id
        if self._is_player_team_yellow():
            player_id -= PLAYER_PER_TEAM
        return player_id


class SetSpeed(_Command):
    def __init__(self, player, pose):
        super().__init__(player)
        self.is_speed_command = True
        pose.orientation = pose.orientation * 180 / math.pi
        self.pose = pose


class MoveTo(_Command):
    def __init__(self, player, position):
        super().__init__(player)
        self.pose.position = position
        self.pose.orientation = player.pose.orientation


class Rotate(_Command):
    def __init__(self, player, orientation):
        super().__init__(player)
        self.pose.orientation = orientation
        self.pose.position = player.pose.position


class MoveToAndRotate(_Command):
    def __init__(self, player, pose):
        super().__init__(player)
        self.pose = pose


class Kick(_Command):
    def __init__(self, player, kick_speed=5):
        super().__init__(player)
        self.kick = True
        self.kick_speed = kick_speed
        self.pose = player.pose


class Dribble(_Command):
    def __init__(self, player, enable=True, dribble_speed=4):
        super().__init__(player)
        self.dribble = enable
        self.dribble_speed = dribble_speed
        self.pose = player.pose


class Stop(_Command):
    def __init__(self, player):
        super().__init__(player)
        self.is_speed_command = True
        self.pose = Pose()
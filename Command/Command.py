import rule

from Util.Pose import Pose


PLAYER_PER_TEAM = 6


class _Command(object):
    def __init__(self, player):
        self.player = player
        self.dribble = False
        self.dribble_speed = 0
        self.kick = False
        self.kick_speed = 0
        self.stop = False
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
        robot_command.stop = self.stop
        robot_command.pose.coord.x = self.pose.position.x
        robot_command.pose.coord.y = self.pose.position.y
        robot_command.pose.orientation = 0 - self.pose.orientation

        return robot_command

    def _is_player_team_yellow(self):
        return self.player.id >= PLAYER_PER_TEAM

    def _get_player_id(self):
        player_id = self.player.id
        if self._is_player_team_yellow():
            player_id -= PLAYER_PER_TEAM
        return player_id


class MoveTo(_Command):
    def __init__(self, player, position):
        super().__init__(player)
        self.pose.position = position


class Rotate(_Command):
    def __init__(self, player, orientation):
        super().__init__(player)
        self.pose.orientation = orientation


class MoveToAndRotate(_Command):
    def __init__(self, player, pose):
        super().__init__(player)
        self.pose = pose


class Kick(_Command):
    def __init__(self, player, kick_speed=1):
        super().__init__(player)
        self.kick = True
        self.kick_speed = kick_speed


class Dribble(_Command):
    def __init__(self, player, dribble_speed=1):
        super().__init__(player)
        self.dribble = True
        self.dribble_speed = dribble_speed
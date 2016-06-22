#Under MIT License, see LICENSE.txt
import math
from ..Util.Pose import Pose, Position
from ..Game.Player import Player
from ..Game.Team import Team
from ..Util.area import *
from ..Util.geometry import *
from ..Util.constant import *


class _Command(object):
    def __init__(self, player):
        assert(isinstance(player, Player))
        self.player = player
        self.dribble = True
        self.dribble_speed = 10
        self.kick = False
        self.kick_speed = 0
        self.is_speed_command = False
        self.pose = Pose()
        self.team = player.team

    def toSpeedCommand(self):
        """
            If is_speed_command is false,
            converts the command to a speed commmand.

            If is_speed_command is true,
            returns the command.

            Always returns self, meaning the command
            may have changed in the process.
        """
        if not self.is_speed_command:
            self.pose = self._convertPositionToSpeed(self.player.pose,
                                                     self.pose)

        return self

    def _convertPositionToSpeed(self, current_pose, next_pose):
        """
            Converts an absolute position to a
            speed command relative to the player.

            :param current_pose: the current position of a player.
            :param next_pose: the absolute position the robot should go to.
            :returns: A Pose object with speed vectors.
        """
        #TODO: Cleanup
        x = next_pose.position.x
        y = next_pose.position.y
        theta = next_pose.orientation
        current_theta = current_pose.orientation
        current_x = current_pose.position.x
        current_y = current_pose.position.y
        theta_direction = theta - current_theta
        if theta_direction >= math.pi:
            theta_direction -= 2 * math.pi
        elif theta_direction <= -math.pi:
            theta_direction += 2*math.pi

        if (theta_direction == 0):
            theta_speed = 0
        elif (abs(theta_direction) > 0.2):
            theta_speed = 2
        elif(abs(theta_direction) <= 0.2 and abs(theta_direction) > 0):
            theta_speed = 0.4
        new_theta = theta_speed if theta_direction >= 0 else -theta_speed

        direction_x = x - current_x
        direction_y = y - current_y
        norm = math.hypot(direction_x, direction_y)
        speed = 1 if norm >= 50 else 0
        if norm:
            direction_x /= norm
            direction_y /= norm
        cosangle = math.cos(-current_theta)
        sinangle = math.sin(-current_theta)
        new_x = (direction_x * cosangle - direction_y * sinangle) * speed
        new_y = (direction_y * cosangle + direction_x * sinangle) * speed

        return Pose(Position(new_x, new_y), new_theta)


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
    def __init__(self, player, position):
        # Parameters Assertion
        assert(isinstance(position, Position))

        super().__init__(player)
        self.pose.position = stayInsideSquare(position,
                                              FIELD_Y_TOP,
                                              FIELD_Y_BOTTOM,
                                              FIELD_X_LEFT,
                                              FIELD_X_RIGHT)
        self.pose.orientation = player.pose.orientation


class Rotate(_Command):
    def __init__(self, player, orientation):
        assert(isinstance(orientation, (int, float)))

        super().__init__(player)
        self.pose.orientation = orientation
        self.pose.position = stayInsideSquare(player.pose.position,
                                              FIELD_Y_TOP,
                                              FIELD_Y_BOTTOM,
                                              FIELD_X_LEFT,
                                              FIELD_X_RIGHT)


class MoveToAndRotate(_Command):
    def __init__(self, player, pose):
        assert(isinstance(pose, Pose))

        super().__init__(player)
        position = stayInsideSquare(pose.position,
                                    FIELD_Y_TOP,
                                    FIELD_Y_BOTTOM,
                                    FIELD_X_LEFT,
                                    FIELD_X_RIGHT)
        self.pose = Pose(position, pose.orientation)


class Kick(_Command):
    def __init__(self, player, kick_speed=5):
        assert(isinstance(player, Player))
        assert(isinstance(kick_speed, (int, float)))
        assert(0 <= kick_speed <= 8)

        super().__init__(player)
        self.kick = True
        self.kick_speed = kick_speed
        self.is_speed_command = True
        self.pose = player.pose


class Stop(_Command):
    def __init__(self, player):
        assert(isinstance(player, Player))

        super().__init__(player)
        self.is_speed_command = True
        self.pose = Pose()

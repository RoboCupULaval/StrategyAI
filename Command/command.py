# Under MIT License, see LICENSE.txt
import math

from ..Util.Pose import Pose, Position
from ..Game.Player import Player
from ..Game.Team import Team
from ..Util.area import *
from ..Util.geometry import *
from ..Util.constant import ORIENTATION_ABSOLUTE_TOLERANCE, SPEED_ABSOLUTE_TOLERANCE, SPEED_DEAD_ZONE_DISTANCE

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

    def _convertPositionToSpeed(self, current_pose, target_pose):
        """
            Converts an absolute position to a
            speed command relative to the player.

            :param current_pose: the current position of a player.
            :param target_pose: the absolute position the robot should go to.
            :returns: A Pose object with speed vectors.
        """
        position = self._compute_position_for_speed_command(current_pose.position, target_pose.position, current_pose.orientation)
        orientation = self._compute_orientation_for_speed_command(current_pose.orientation, target_pose.orientation)

        return Pose(position, orientation)


    def _compute_position_for_speed_command(self, current_position, target_position, current_theta):
        target_x = target_position.x
        target_y = target_position.y
        current_x = current_position.x
        current_y = current_position.y

        delta_x = target_x - current_x
        delta_y = target_y - current_y
        norm = math.hypot(delta_x, delta_y)

        speed = 1 if norm >= SPEED_DEAD_ZONE_DISTANCE else 0

        if norm > 0:
            delta_x /= norm
            delta_y /= norm
        else:
            delta_x = 0
            delta_y = 0

        return Position(delta_x, delta_y, abs_tol=SPEED_ABSOLUTE_TOLERANCE) * speed


    def _compute_orientation_for_speed_command(self, current_orientation, target_orientation):

        theta_direction = self._compute_theta_direction(current_orientation, target_orientation)
        theta_speed = self._compute_theta_speed(theta_direction)

        return theta_speed if theta_direction >= 0 else -theta_speed


    def _compute_theta_direction(self, current_theta, target_theta):
        """
            Trouve le sens de rotation le plus efficient.

            Par exemple: current_theta = 30 deg et target_theta = 10 deg -> -20 deg de rotation (plutôt que 340 deg)
        """

        theta_direction = target_theta - current_theta
        if theta_direction >= math.pi:
            theta_direction -= 2 * math.pi
        elif theta_direction <= -math.pi:
            theta_direction += 2*math.pi
        return theta_direction

    def _compute_theta_speed(self, theta_direction):
        # FIXME: magic number!
        # TODO: Mettre un cutoff puis calculer la vitesse de rotation selon une formule pour obtenir une courbe
        if math.isclose(theta_direction, 0, abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE):
            return 0
        elif abs(theta_direction) > 0.2:
            return 2 # pourquoi 2? qu'est-ce que sa représente?
        elif abs(theta_direction) < 0.2 or math.isclose(abs(theta_direction), 0.2, abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE):
            return 0.4 # même question ...


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
    def __init__(self, player, kick_speed=0.5):
        """ Kick speed est un float entre 0 et 1 """
        assert(isinstance(player, Player))
        assert(isinstance(kick_speed, (int, float)))
        assert(0 <= kick_speed <= 1)
        kick_speed = kick_speed * KICK_MAX_SPD

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

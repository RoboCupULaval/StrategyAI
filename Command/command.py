# Under MIT License, see LICENSE.txt
"""
    Ce module permet de créer des commandes pour faire agir les robots.
    Des fonctions utilitaire permettent de transformer une commande de
    Position (Pose) en une commande de vitesse.

    L'embarqué et le simulateur utilise un vecteur de vitesse (Pose) pour
    contrôler les robots.
"""
import math

from ..Util.Pose import Pose, Position
from ..Game.Player import Player
from ..Game.Team import Team
from ..Util.area import *
from ..Util.geometry import *

DEFAULT_STATIC_GAIN = 0.00095
DEFAULT_INTEGRAL_GAIN = 0.0009
DEFAULT_THETA_GAIN = 0.01
MAX_INTEGRAL_PART = 45000
MAX_NAIVE_CMD = math.sqrt(2)/3
MIN_NAIVE_CMD = -math.sqrt(2)/3
MAX_THETA_CMD = math.pi/8
MIN_THETA_CMD = -math.pi/8

def _correct_for_referential_frame(x, y, orientation):
    cos = math.cos(-orientation)
    sin = math.sin(-orientation)

    corrected_x = (x * cos - y * sin)
    corrected_y = (y * cos + x * sin)
    return corrected_x, corrected_y

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
        self.stop_cmd = False


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
        self.stop_cmd = True

class PI(object):
    """
        Asservissement PI en position

        u = up + ui
    """

    def __init__(self, static_gain=DEFAULT_STATIC_GAIN, integral_gain=DEFAULT_INTEGRAL_GAIN, theta_gain=DEFAULT_THETA_GAIN):
        self.accumulator_x = 0
        self.accumulator_y = 0
        self.kp = static_gain
        self.ki = integral_gain
        self.ktheta = theta_gain
        self.last_command_x = 0
        self.last_command_y = 0

    def update_pid_and_return_speed_command(self, position_command):
        """ Met à jour les composants du pid et retourne une commande en vitesse. """
        r_x, r_y = position_command.pose.position.x, position_command.pose.position.y
        t_x, t_y = position_command.player.pose.position.x, position_command.player.pose.position.y
        e_x = r_x - t_x
        e_y = r_y - t_y

        # composante proportionnel
        up_x = self.kp * e_x
        up_y = self.kp * e_y

        # composante integrale
        ui_x = self.ki * e_x
        ui_y = self.ki * e_y
        self.accumulator_x = self.accumulator_x + ui_x
        self.accumulator_y = self.accumulator_y + ui_y
        ui_x = ui_x if ui_x < MAX_INTEGRAL_PART else MAX_INTEGRAL_PART
        ui_y = ui_y if ui_y < MAX_INTEGRAL_PART else MAX_INTEGRAL_PART

        u_x = up_x + ui_x
        u_y = up_y + ui_y

        # correction frame referentiel et saturation
        x, y = _correct_for_referential_frame(u_x, u_y, position_command.player.pose.orientation)
        x = x if x < MAX_NAIVE_CMD else MAX_NAIVE_CMD
        x = x if x > MIN_NAIVE_CMD else MIN_NAIVE_CMD
        y = y if y < MAX_NAIVE_CMD else MAX_NAIVE_CMD
        y = y if y > MIN_NAIVE_CMD else MIN_NAIVE_CMD

        # correction de theta
        e_theta = 0 - position_command.player.pose.orientation
        theta = self.ktheta * e_theta
        theta = theta if theta < MAX_THETA_CMD else MAX_THETA_CMD
        theta = theta if theta > MIN_THETA_CMD else MIN_THETA_CMD

        cmd = Pose(Position(x, y), theta)
        if position_command.stop_cmd:
            cmd = Pose(Position(0, 0))

        return cmd

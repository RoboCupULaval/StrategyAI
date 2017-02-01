# Under MIT License, see LICENSE.txt
"""
    Ce module permet de créer des commandes pour faire agir les robots.
    Des fonctions utilitaire permettent de transformer une commande de
    Position (Pose) en une commande de vitesse.

    L'embarqué et le simulateur utilise un vecteur de vitesse (Pose) pour
    contrôler les robots.
"""
import math

from ..Game.Player import Player
from ..Util.area import *

INTEGRAL_DECAY = 0.981  # réduit de moitié à toutes les 10 itérations
ZERO_ACCUMULATOR_TRHESHOLD = 0.5
FILTER_LENGTH = 1

SIMULATION_MAX_NAIVE_CMD = math.sqrt(2) / 3
SIMULATION_MIN_NAIVE_CMD = -math.sqrt(2) / 3
SIMULATION_MAX_THETA_CMD = math.pi / 8
SIMULATION_MIN_THETA_CMD = 0
SIMULATION_DEFAULT_STATIC_GAIN = 0.00095
SIMULATION_DEFAULT_INTEGRAL_GAIN = 0.0009
SIMULATION_DEFAULT_THETA_GAIN = 1

REAL_MAX_NAIVE_CMD = 1200
REAL_MIN_NAIVE_CMD = 80
REAL_MAX_THETA_CMD = 0
REAL_MIN_THETA_CMD = 0
REAL_DEFAULT_STATIC_GAIN = 0.325
REAL_DEFAULT_INTEGRAL_GAIN = 0.350
REAL_DEFAULT_THETA_GAIN = 100


def _correct_for_referential_frame(x, y, orientation):
    cos = math.cos(-orientation)
    sin = math.sin(-orientation)

    corrected_x = (x * cos - y * sin)
    corrected_y = (y * cos + x * sin)
    return corrected_x, corrected_y


class _Command(object):
    def __init__(self, player):
        assert (isinstance(player, Player))
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
        assert (isinstance(position, Position))

        super().__init__(player)
        self.pose.position = stayInsideSquare(position,
                                              FIELD_Y_TOP,
                                              FIELD_Y_BOTTOM,
                                              FIELD_X_LEFT,
                                              FIELD_X_RIGHT)
        self.pose.orientation = player.pose.orientation


class Rotate(_Command):
    def __init__(self, player, orientation):
        assert (isinstance(orientation, (int, float)))

        super().__init__(player)
        self.pose.orientation = orientation
        self.pose.position = stayInsideSquare(player.pose.position,
                                              FIELD_Y_TOP,
                                              FIELD_Y_BOTTOM,
                                              FIELD_X_LEFT,
                                              FIELD_X_RIGHT)


class MoveToAndRotate(_Command):
    def __init__(self, player, pose):
        assert (isinstance(pose, Pose))

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
        assert (isinstance(player, Player))
        assert (isinstance(kick_speed, (int, float)))
        assert (0 <= kick_speed <= 1)
        kick_speed = kick_speed * KICK_MAX_SPD

        super().__init__(player)
        self.kick = True
        self.kick_speed = kick_speed
        self.is_speed_command = True
        self.pose = player.pose


class Stop(_Command):
    def __init__(self, player):
        assert (isinstance(player, Player))

        super().__init__(player)
        self.is_speed_command = True
        self.pose = Pose()
        self.stop_cmd = True


class PI(object):
    """
        Asservissement PI en position

        u = Kp * err + Sum(err) * Ki * dt
    """

    def __init__(self, simulation_setting=True):
        self.accumulator_x = 0
        self.accumulator_y = 0
        self.constants = _set_constants(simulation_setting)
        self.kp = self.constants['default-kp']
        self.ki = self.constants['default-ki']
        self.ktheta = self.constants['default-ktheta']
        self.last_command_x = 0
        self.last_command_y = 0
        self.previous_cmd = []

    def update_pid_and_return_speed_command(self, position_command, delta_t=0.030):
        """ Met à jour les composants du pid et retourne une commande en vitesse. """
        r_x, r_y = position_command.pose.position.x, position_command.pose.position.y
        t_x, t_y = position_command.player.pose.position.x, position_command.player.pose.position.y
        e_x = r_x - t_x
        e_y = r_y - t_y

        # composante proportionnel
        up_x = self.kp * e_x
        up_y = self.kp * e_y

        # composante integrale, decay l'accumulator
        ui_x, ui_y = self._compute_integral(delta_t, e_x, e_y)
        if position_command.player.id == 4:
            # TODO: retirer une fois le raffinage complete
            # print("Valeur des accumulateurs: {} -- {}".format(self.accumulator_x, self.accumulator_y))
            pass
        self._zero_accumulator()

        u_x = up_x + ui_x
        u_y = up_y + ui_y

        # correction frame reference et saturation
        x, y = self._referential_correction_saturation(position_command, u_x, u_y)

        # correction de theta
        e_theta = position_command.pose.orientation - position_command.player.pose.orientation
        theta = self.ktheta * e_theta
        theta = self._saturate_orientation(theta)

        cmd = Pose(Position(x, y), theta)
        if position_command.stop_cmd:
            cmd = Pose(Position(0, 0))

        cmd = self._filter_cmd(cmd)
        cmd.orientation = theta
        return cmd

    def _saturate_orientation(self, theta):
        if abs(theta) > self.constants['max-theta-cmd']:
            if theta > 0:
                return self.constants['max-theta-cmd']
            else:
                return -self.constants['max-theta-cmd']
        elif abs(theta) < self.constants['min-theta-cmd']:
                return 0
        else:
            return theta

    def _referential_correction_saturation(self, position_command, u_x, u_y):
        x, y = _correct_for_referential_frame(u_x, u_y, position_command.player.pose.orientation)

        if abs(x) > self.constants['max-naive-cmd']:
            if x > 0:
                x = self.constants['max-naive-cmd']
            else:
                x = -self.constants['max-naive-cmd']

        if abs(x) < self.constants['min-naive-cmd']:
            x = 0

        if abs(y) > self.constants['max-naive-cmd']:
            if y > 0:
                y = self.constants['max-naive-cmd']
            else:
                y = -self.constants['max-naive-cmd']

        if abs(y) < self.constants['min-naive-cmd']:
            y = 0

        return x, y

    def _compute_integral(self, delta_t, e_x, e_y):
        ui_x = self.ki * e_x * delta_t
        ui_y = self.ki * e_y * delta_t
        self.accumulator_x = (self.accumulator_x * INTEGRAL_DECAY * delta_t) + ui_x
        self.accumulator_y = (self.accumulator_y * INTEGRAL_DECAY * delta_t) + ui_y
        return ui_x, ui_y

    def _zero_accumulator(self):
        if self.accumulator_x < ZERO_ACCUMULATOR_TRHESHOLD:
            self.accumulator_x = 0

        if self.accumulator_y < ZERO_ACCUMULATOR_TRHESHOLD:
            self.accumulator_y = 0

    def _filter_cmd(self, cmd):
        self.previous_cmd.append(cmd)
        xsum = 0
        ysum = 0
        for cmd in self.previous_cmd:
            xsum += cmd.position.x
            ysum += cmd.position.y

        xsum /= len(self.previous_cmd)
        ysum /= len(self.previous_cmd)
        if len(self.previous_cmd) > FILTER_LENGTH:
            self.previous_cmd.pop(0)
        return Pose(Position(xsum, ysum))


def _set_constants(simulation_setting):
    if simulation_setting:
        return {'max-naive-cmd':SIMULATION_MAX_NAIVE_CMD,
                'min-naive-cmd':SIMULATION_MIN_NAIVE_CMD,
                'max-theta-cmd':SIMULATION_MAX_THETA_CMD,
                'min-theta-cmd':SIMULATION_MIN_THETA_CMD,
                'default-kp':SIMULATION_DEFAULT_STATIC_GAIN,
                'default-ki':SIMULATION_DEFAULT_INTEGRAL_GAIN,
                'default-ktheta':SIMULATION_DEFAULT_THETA_GAIN
                }
    else:
        return {'max-naive-cmd':REAL_MAX_NAIVE_CMD,
                'min-naive-cmd':REAL_MIN_NAIVE_CMD,
                'max-theta-cmd':REAL_MAX_THETA_CMD,
                'min-theta-cmd':REAL_MIN_THETA_CMD,
                'default-kp':REAL_DEFAULT_STATIC_GAIN,
                'default-ki':REAL_DEFAULT_INTEGRAL_GAIN,
                'default-ktheta':REAL_DEFAULT_THETA_GAIN
                }

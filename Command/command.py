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
from ..Util.constant import ORIENTATION_ABSOLUTE_TOLERANCE, SPEED_ABSOLUTE_TOLERANCE, SPEED_DEAD_ZONE_DISTANCE, DEFAULT_MAX_SPEED, DEFAULT_MIN_SPEED

DEFAULT_STATIC_GAIN = 0.00095
DEFAULT_INTEGRAL_GAIN = 0.0001
DEFAULT_THETA_GAIN = 0.01
MAX_INTEGRAL_PART = 500
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

    def to_speed_command(self):
        """
            Transforme la commande en une commande de vitesse (SpeedCommand)
            et affecte le drapeau.
        """
        if not self.is_speed_command:
            self.pose = self._convert_position_to_speed(self.player.pose, self.pose)

        return self

    def _convert_position_to_speed(self, current_pose, target_pose, deadzone=SPEED_DEAD_ZONE_DISTANCE, max_speed=DEFAULT_MAX_SPEED, min_speed=DEFAULT_MIN_SPEED):
        """
            Converts an absolute position to a
            speed command relative to the player.

            :param current_pose: the current position of a player.
            :param target_pose: the absolute position the robot should go to.
            :returns: A Pose object with speed vectors.
        """
        position = self._compute_position_for_speed_command(current_pose.position, target_pose.position, current_pose.orientation, deadzone, max_speed, min_speed)
        orientation = self._compute_orientation_for_speed_command(current_pose.orientation, target_pose.orientation)

        return Pose(position, orientation)


    def _compute_position_for_speed_command(self, current_position, target_position, current_theta, deadzone=SPEED_DEAD_ZONE_DISTANCE, max_speed=DEFAULT_MAX_SPEED, min_speed=DEFAULT_MIN_SPEED):
        """
            Calcul la différence en x et en y entre la position actuelle et la position cible.
            La norme du delta_x et delta_y calculé est normalisée.
            Si la norme, qui représente la distance dans ce contexte, est supérieur à une deadzone, on retourne zéro.
            La position est aussi réglée pour avoir une tolérance de 3 décimales.
        """
        target_x = target_position.x
        target_y = target_position.y
        current_x = current_position.x
        current_y = current_position.y

        delta_x = target_x - current_x
        delta_y = target_y - current_y
        distance = math.hypot(delta_x, delta_y)

        speed = self._compute_speed_from_distance(distance, deadzone, max_speed, min_speed)
        if self.player.id == 4:
            print("Speed: " + str(speed))

        if distance > 0:
            delta_x /= distance
            delta_y /= distance
        else:
            delta_x = 0
            delta_y = 0

        speed_x, speed_y = _correct_for_referential_frame(delta_x, delta_y, current_theta)

        return Position(speed_x, speed_y, abs_tol=SPEED_ABSOLUTE_TOLERANCE) * speed


    def _compute_orientation_for_speed_command(self, current_orientation, target_orientation):
        """
            On trouve une orientation [-pi, pi] en choississant le plus petit delta_direction.
            La valeur de retour est un magic number, soit {0, 0.4, 2}.
        """

        delta_theta = self._compute_optimal_delta_theta(current_orientation, target_orientation)
        theta_speed = self._compute_theta_speed(delta_theta)

        return theta_speed if delta_theta >= 0 else -theta_speed

    def _compute_speed_from_distance(self, distance, deadzone=SPEED_DEAD_ZONE_DISTANCE, max_speed=DEFAULT_MAX_SPEED, min_speed=DEFAULT_MIN_SPEED):
        speed = 0
        if distance >= deadzone:
            speed = max_speed
        else :
            speed = math.sqrt(distance * (max_speed/deadzone))

        speed = self._saturate_speed(speed, max_speed, min_speed)
        return speed

    def _saturate_speed(self, speed, max_speed=DEFAULT_MAX_SPEED, min_speed=DEFAULT_MIN_SPEED):
        speed = speed if speed < max_speed else max_speed
        return speed if speed > min_speed else min_speed


    def _compute_optimal_delta_theta(self, current_theta, target_theta):
        """
            Trouve l'angle de rotation le plus optimal.

            Par exemple: current_theta = 30 deg et target_theta = 10 deg -> -20 deg de rotation (plutôt que 340 deg)
            NB: L'exemple est écrit en degrées, mais tous les calculs sont effectués en radians
        """
        delta_theta = target_theta - current_theta
        optimal_delta_theta = 0

        if delta_theta >= math.pi:
            optimal_delta_theta = delta_theta - 2 * math.pi
        elif delta_theta <= -math.pi:
            optimal_delta_theta = delta_theta + 2*math.pi
        else:
            optimal_delta_theta = delta_theta

        return optimal_delta_theta

    def _compute_theta_speed(self, delta_theta):
        """ MAGIC NUMBER !!! """
        # FIXME: magic number!
        # TODO: Mettre un cutoff puis calculer la vitesse de rotation selon une formule pour obtenir une courbe
        if math.isclose(delta_theta, 0, abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE):
            return 0
        elif abs(delta_theta) > 0.2:
            return 2 # pourquoi 2? qu'est-ce que sa représente?
        elif abs(delta_theta) < 0.2 or math.isclose(abs(delta_theta), 0.2, abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE):
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

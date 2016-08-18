# Under MIT License, see LICENSE.txt
import unittest
import math
import functools

from RULEngine.Command.command import _Command
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import ORIENTATION_ABSOLUTE_TOLERANCE

class TestCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = _Command(Player(None, 0))
        # uut fonction spécial que certains test modifient pour simplifier les autres tests
        # fyi: uut -> unit under test
        self.uut = None

    def test_convert_position_to_speed_orientation(self):
        """ Diverses tests pour valider l'orientation obtenu dans la Speed """
        self.uut = functools.partial(self.cmd._convertPositionToSpeed, Pose())

        # sanity
        self.assertFalse(self.uut(Pose()) == Pose(Position(), 1.57))

        speed_self = self.uut(Pose())
        self.assertEqual(speed_self, Pose())
        speed_self_rotate1 = self.uut(Pose(Position(), math.pi/2))
        self.assertEqual(speed_self_rotate1, Pose(Position(), 2))
        speed_self_rotate2 = self.uut(Pose(Position(), math.pi))
        self.assertEqual(speed_self_rotate2, Pose(Position(), 2))
        speed_self_rotate3 = self.uut(Pose(Position(), 3*math.pi/2))
        self.assertEqual(speed_self_rotate3, Pose(Position(), -2))
        speed_self_rotate8 = self.uut(Pose(Position(), math.pi+ORIENTATION_ABSOLUTE_TOLERANCE))
        self.assertEqual(speed_self_rotate8, Pose(Position(), -2)) # test edge case transition rotation negative
        speed_self_rotate4 = self.uut(Pose(Position(), 0.20))
        self.assertEqual(speed_self_rotate4, Pose(Position(), 0.4))
        speed_self_rotate5 = self.uut(Pose(Position(), 0.19))
        self.assertEqual(speed_self_rotate5, Pose(Position(), 0.4))
        speed_self_rotate6 = self.uut(Pose(Position(), -0.20))
        self.assertEqual(speed_self_rotate6, Pose(Position(), -0.4))
        speed_self_rotate7 = self.uut(Pose(Position(), -0.19))
        self.assertEqual(speed_self_rotate7, Pose(Position(), -0.4))

    def test_convert_position_to_speed_position(self):
        """
            Test de la Position obtenu dans la Speed.

            NB: Une Position par défaut ne compare pas les décimales et les Position obtenus
            ont des composantes inférieur à 1, il faut donc changer lors de la construction des Pose la tolérance absolu
            de la Position (l'un ou l'autre est suffisant).
        """
        self.uut = functools.partial(self.cmd._convertPositionToSpeed, Pose())

        # sanity
        self.assertNotEqual(self.uut(Pose()), Pose(Position(1234, -543, abs_tol=1e-3), 0))

        speed_pose_I = self.uut(Pose(Position(900, 900), 0))
        self.assertEqual(speed_pose_I, Pose(Position(math.sqrt(2)/2, math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose_II = self.uut(Pose(Position(-900, 900), 0))
        self.assertEqual(speed_pose_II, Pose(Position(-math.sqrt(2)/2, math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose_III = self.uut(Pose(Position(-900, -900), 0))
        self.assertEqual(speed_pose_III, Pose(Position(-math.sqrt(2)/2, -math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose_IV = self.uut(Pose(Position(900, -900), 0))
        self.assertEqual(speed_pose_IV, Pose(Position(math.sqrt(2)/2, -math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose = self.uut(Pose(Position(1000, 300), 0))
        self.assertEqual(speed_pose, Pose(Position(0.957, 0.287, abs_tol=1e-3), 0))
        speed_pose = self.uut(Pose(Position(300, 1000), 0))
        self.assertEqual(speed_pose, Pose(Position(0.287, 0.957, abs_tol=1e-3), 0))

    def test_compute_theta_direction(self):
        """ Test du calcul de theta_direction, 4 décimales de précisions. """
        self.uut = functools.partial(self.cmd._compute_theta_direction, 0)
        # sanity
        self.assertNotAlmostEqual(self.uut(0), math.pi, 4)
        self.assertNotAlmostEqual(self.uut(math.pi), 0, 4)

        self.assertAlmostEqual(self.uut(math.pi/2), math.pi/2, 4)
        self.assertAlmostEqual(self.uut(math.pi-0.5), math.pi-0.5, 4)
        self.assertAlmostEqual(self.uut(math.pi), -math.pi, 4) # NB: par construction, favorise de resotir une orientation négative, sensible à la comparaison de float
        self.assertAlmostEqual(self.uut(-math.pi), math.pi, 4)
        self.assertNotAlmostEqual(self.uut(math.pi), self.uut(-math.pi), 4)
        self.assertAlmostEqual(self.uut(math.pi+0.5), -math.pi+0.5, 4)
        self.assertAlmostEqual(self.uut(-math.pi/2), -math.pi/2, 4)

# Under MIT License, see LICENSE.txt
import unittest
import math
import functools

from RULEngine.Command.command import _Command, _correct_for_referential_frame
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import ORIENTATION_ABSOLUTE_TOLERANCE, SPEED_ABSOLUTE_TOLERANCE

class TestCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = _Command(Player(None, 0))
        # uut fonction spécial que certains test modifient pour simplifier les autres tests
        # fyi: uut -> unit under test
        self.uut = None

    def test_convert_position_to_speed_orientation(self):
        """ Diverses tests pour valider l'orientation obtenu dans la Speed """
        self.uut = functools.partial(self.cmd._convert_position_to_speed, Pose())

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
        self.uut = functools.partial(self.cmd._convert_position_to_speed, Pose(), deadzone=100, max_speed=1, min_speed=0.1)

        # sanity
        self.assertNotEqual(self.uut(Pose()), Pose(Position(1234, -543, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))

        speed_pose_I = self.uut(Pose(Position(900, 900), 0))
        self.assertEqual(speed_pose_I, Pose(Position(math.sqrt(2)/2, math.sqrt(2)/2, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))
        speed_pose_II = self.uut(Pose(Position(-900, 900), 0))
        self.assertEqual(speed_pose_II, Pose(Position(-math.sqrt(2)/2, math.sqrt(2)/2, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))
        speed_pose_III = self.uut(Pose(Position(-900, -900), 0))
        self.assertEqual(speed_pose_III, Pose(Position(-math.sqrt(2)/2, -math.sqrt(2)/2, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))
        speed_pose_IV = self.uut(Pose(Position(900, -900), 0))
        self.assertEqual(speed_pose_IV, Pose(Position(math.sqrt(2)/2, -math.sqrt(2)/2, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))
        speed_pose = self.uut(Pose(Position(1000, 300), 0))
        self.assertEqual(speed_pose, Pose(Position(0.957, 0.287, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))
        speed_pose = self.uut(Pose(Position(300, 1000), 0))
        self.assertEqual(speed_pose, Pose(Position(0.287, 0.957, abs_tol=SPEED_ABSOLUTE_TOLERANCE), 0))

        # test pour frame de ref
        self.uut = functools.partial(self.cmd._convert_position_to_speed, Pose(Position(0, 0, abs_tol=1e-4), math.pi/2), deadzone=100, max_speed=1, min_speed=0.1)
        # sanity
        self.assertNotEqual(self.uut(Pose(Position(500, 0))).position, Position(1, 0, abs_tol=1e-4))
        self.assertEqual(self.uut(Pose(Position(500, 0))).position, Position(6.1232e-17, -1.0000, abs_tol=1e-4))

    def test_compute_optimal_delta_theta(self):
        """ Test du calcul de theta_direction, 4 décimales de précisions. """
        self.uut = functools.partial(self.cmd._compute_optimal_delta_theta, 0)
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

    def test_compute_theta_speed(self):
        """
            Test des magic numbers ...

            Les résultats possible sont fixe, même s'ils peuvent être des float, on utilise des assertEqual
        """
        self.uut = functools.partial(self.cmd._compute_theta_speed) # techniquement inutile, on pourrait assigner directement

        # sanity
        self.assertNotEqual(self.uut(math.pi/2), 0)

        self.assertEqual(self.uut(0), 0)
        self.assertEqual(self.uut(0.0001), 0)
        self.assertEqual(self.uut(-0.0001), 0)

        self.assertEqual(self.uut(0.2000001), 2)
        self.assertEqual(self.uut(2), 2)
        self.assertEqual(self.uut(-2), 2)
        self.assertEqual(self.uut(-0.2000001), 2)

        self.assertEqual(self.uut(0.1999999), 0.4)
        self.assertEqual(self.uut(-0.1999999), 0.4)
        self.assertEqual(self.uut(0.0005), 0.4)

    def test_correct_for_referential_frame(self):
        """
            Test pour valider que le changement d'axes de référence est bien calculé.
        """
        self.uut = functools.partial(_correct_for_referential_frame, 0.5, 0.5)
        x1, y1 = self.uut(0)
        x2, y2 = self.uut(math.pi)
        x3, y3 = self.uut((2*math.pi)/1000)
        self.assertNotEqual(Position(x1, y1, abs_tol=1e-2), Position(x2, y2))
        self.assertEqual(Position(x1, y1, abs_tol=1e-2), Position(x3, y3))

        x4, y4 = self.uut((math.pi/2 + 0.47))
        self.assertEqual(Position(x4, y4, abs_tol=1e-2), Position(0.21, -0.67))

    def test_saturate_speed(self):
        """
            Test la fonction qui sature la vitesse
        """
        self.uut = functools.partial(self.cmd._saturate_speed, max_speed=1.0, min_speed=0.1)
        self.assertNotAlmostEqual(self.uut(0.9), self.uut(0.2))

        self.assertAlmostEqual(self.uut(1), self.uut(2))
        self.assertAlmostEqual(self.uut(2), self.uut(100))
        self.assertAlmostEqual(self.uut(-1), self.uut(0.1))
        self.assertAlmostEqual(self.uut(-1), self.uut(-147))
        self.assertAlmostEqual(self.uut(0.09), self.uut(0.1))
        self.assertAlmostEqual(self.uut(1.01), self.uut(1))

        self.uut = functools.partial(self.cmd._saturate_speed, max_speed=1.41, min_speed=0.42)
        self.assertNotAlmostEqual(self.uut(1.40), self.uut(0.43))
        self.assertAlmostEqual(self.uut(2), self.uut(1.41))
        self.assertAlmostEqual(self.uut(0.42), self.uut(0.3))

    def test_compute_speed_from_distance(self):
        """
            Test de la fonction qui réduit progressivement la vitesse lorsqu'on
            approche de la target.
        """
        self.uut = functools.partial(self.cmd._compute_speed_from_distance, deadzone=100, max_speed=1, min_speed=0.3)
        self.assertNotAlmostEqual(self.uut(50), self.uut(90))

        self.assertAlmostEqual(self.uut(50), self.uut(50))
        self.assertAlmostEqual(self.uut(50), math.sqrt(0.5))
        self.assertAlmostEqual(self.uut(42), math.sqrt(0.42))
        self.assertAlmostEqual(self.uut(101), 1)
        self.assertAlmostEqual(self.uut(9), 0.3)

        self.assertNotAlmostEqual(self.cmd._compute_speed_from_distance(50, 100, 1, 0.1), self.cmd._compute_speed_from_distance(50, 150, 1, 0.1))

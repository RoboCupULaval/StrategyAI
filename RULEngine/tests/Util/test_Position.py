import unittest

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import compare_angle

import numpy as np
import math as m


class TestPosition(unittest.TestCase):

    def test_new(self):

        self.assertFalse(Position(900, 900) == Position())  # sanity check

        self.assertTrue(hasattr(Position(), 'z'))
        self.assertTrue(hasattr(Position(), 'abs_tol'))

        # Init from nothing
        self.assertEqual(Position(), Position(0, 0))
        self.assertTrue(Position().z == 0)
        self.assertTrue(Position(0, 0).z == 0)
        pos0 = Position(z=1)
        self.assertTrue(pos0.z == 1)

        # Init from positional argument
        pos1 = Position(0, 0)
        self.assertEqual(pos1.x, 0)
        self.assertEqual(pos1.y, 0)
        self.assertEqual(pos1.z, 0)

        pos2 = Position(-100, 0.001)
        self.assertEqual(pos2.x, -100)
        self.assertEqual(pos2.y, 0.001)
        self.assertEqual(pos2.z, 0)

        # Init from ndarray
        my_array = np.array([100, -50.23])
        pos3 = Position(np.array(my_array))
        self.assertEqual(pos3.x, 100)
        self.assertEqual(pos3.y, -50.23)
        self.assertEqual(pos3.z, 0)
        my_array[0] = 10
        self.assertFalse(pos3.x == 10)

        # Init from list
        my_list = [9, 10]
        pos4 = Position(my_list)
        self.assertEqual(pos4.x, 9)
        self.assertEqual(pos4.y, 10)
        self.assertEqual(pos4.z, 0)
        my_list[0] = 10
        self.assertFalse(pos4[0] == 10)

        # Init from tuple
        my_tuple = (9, 10)
        pos5 = Position(my_tuple)
        self.assertEqual(pos5.x, 9)
        self.assertEqual(pos5.y, 10)
        self.assertEqual(pos5.z, 0)
        pos5[0] = 10
        self.assertTrue(pos5[0] == 10)

        # Init from another Position
        pos6 = Position(1, 1)
        pos7 = Position(pos6)
        self.assertEqual(pos6, pos7)
        self.assertFalse(pos6 is pos7)
        pos6[1] = 9
        self.assertNotEqual(pos6, pos7)

        with self.assertRaises(ValueError):
            Position(0)
        with self.assertRaises(ValueError):
            Position({})
        with self.assertRaises(ValueError):
            Position(Pose())
        with self.assertRaises(ValueError):
            Position(0, 0, 0)
        with self.assertRaises(ValueError):
            Position([])
        with self.assertRaises(ValueError):
            Position([0])
        with self.assertRaises(ValueError):
            Position([0, 0, 0])
        with self.assertRaises(ValueError):
            Position(())
        with self.assertRaises(ValueError):
            Position((0, 0, 0))
        with self.assertRaises(ValueError):
            Position(np.zeros(1))
        with self.assertRaises(ValueError):
            Position(np.zeros(3))

    def test_get_set(self):

        pos = Position(1, 2, z=3, abs_tol=4)
        self.assertTrue(pos.x == 1)
        self.assertTrue(pos.y == 2)
        self.assertTrue(pos.z == 3)
        self.assertTrue(pos.abs_tol == 4)
        self.assertTrue(pos[0] == 1)
        self.assertTrue(pos[1] == 2)
        pos.x = 4
        pos.y = 3
        pos.z = 2
        pos.abs_tol = 1
        self.assertTrue(pos.x == 4)
        self.assertTrue(pos.y == 3)
        self.assertTrue(pos.z == 2)
        self.assertTrue(pos.abs_tol == 1)
        self.assertTrue(pos[0] == 4)
        self.assertTrue(pos[1] == 3)

    def test_norm(self):
        self.assertEqual(Position().norm(), 0)
        self.assertEqual(Position(1, 1).norm(), m.sqrt(2))
        self.assertEqual(Position(1, -1).norm(), m.sqrt(2))
        self.assertEqual(Position(-1, 1).norm(), m.sqrt(2))
        self.assertEqual(Position(3, 4).norm(), 5)

    def test_angle(self):
        angle = np.arange(-720, 720, 30) * m.pi / 180
        for i in range(angle.size):
            self.assertTrue(compare_angle(Position(m.cos(angle[i]), m.sin(angle[i])).angle(), angle[i]))

        with self.assertWarns(UserWarning):
            Position().angle()

    def test_rotate(self):
        self.assertEqual(Position(1, 0).rotate(0), Position(1, 0))
        self.assertEqual(Position(1, 0).rotate(m.pi/2), Position(0, 1))
        self.assertEqual(Position(0, 1).rotate(m.pi/2), Position(-1, 0))
        self.assertEqual(Position(-1, 0).rotate(m.pi/2), Position(0, -1))
        self.assertEqual(Position(0, -1).rotate(m.pi/2), Position(1, 0))
        self.assertEqual(Position(526, 878).rotate(2.14675), Position(-1022.833, -37.052))

    def test_normalized(self):
        self.assertEqual(Position(1, 0).normalized(), Position(1, 0))
        self.assertEqual(Position(0, -1).normalized(), Position(0, -1))
        self.assertEqual(Position(10, 10).normalized(), Position(m.sqrt(2)/2, m.sqrt(2)/2))
        normalized_vector = Position(np.array([12.45, -23.23]) / np.sqrt(np.square([12.45, -23.23]).sum()))
        self.assertEqual(Position(12.45, -23.23).normalized(), normalized_vector)

        with self.assertRaises(ZeroDivisionError):
            Position(0, 0).normalized()

    def test_eq(self):

        pos1 = Position()
        pos2 = Position()
        self.assertEqual(pos1, pos2)
        self.assertEqual(pos2, pos1)

        pos3 = Position(500, 549)
        pos4 = Position(400, -400)
        pos5 = Position(-500, 400)
        pos6 = Position(0.5, 0.0)
        self.assertFalse(pos3 == pos4)
        self.assertFalse(pos3 == pos5)
        self.assertFalse(pos3 == pos6)

        pos7 = Position(0.5, 0.0, abs_tol=1)
        pos8 = Position(0.0, -0.5, abs_tol=1)
        pos9 = Position(1.0, -1.0, abs_tol=1)
        self.assertTrue(pos7 == pos8)
        self.assertTrue(pos7 == pos9)

        pos10 = Position(0.5, 0.0, abs_tol=1)
        pos11 = Position(-0.5, 0.0, abs_tol=1)
        pos12 = Position(1.0, 0.0, abs_tol=1)
        self.assertTrue(pos10 == pos11)
        self.assertTrue(pos10 == pos12)

        pos11.abs_tol = 0.1
        pos10.abs_tol = 0.1
        self.assertFalse(pos11 == pos10)
        self.assertFalse(pos10 == pos11)

        pos13 = Position(4, 5)
        pos14 = Position(1, 1)

        pose1 = Pose(Position(0, 0), 0)
        pose2 = Pose(pos13, 0)

        self.assertTrue(pose1 == pos1)

        self.assertTrue(pose2 == pos13)
        self.assertTrue(pos1 == pose1)
        self.assertTrue(pos13 == pose2)
        self.assertTrue(pose1 == pos1)

        self.assertFalse(pose1 == pos13)
        self.assertFalse(pose2 == pos1)
        self.assertFalse(pose2 == pos14)
        self.assertFalse(pos14 == pose2)

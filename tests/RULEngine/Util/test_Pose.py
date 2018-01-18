import math as m
import unittest

import numpy as np
from RULEngine.Util.Pose import Pose

from Util import Position


class TestPose(unittest.TestCase):

    def test_init(self):
        #  Default case
        pose = Pose()
        self.assertTrue(hasattr(pose, 'position'))
        self.assertTrue(hasattr(pose, 'orientation'))
        self.assertTrue(type(pose.position) is Position)
        self.assertTrue(type(pose.orientation) is float)

        #  From another Pose
        pose1 = Pose(Position(1, 1), 1)
        pose2 = Pose(pose1)
        self.assertEqual(pose1.position, pose2.position)
        self.assertEqual(pose1.orientation, pose2.orientation)
        self.assertTrue(pose1 is not pose2)
        self.assertTrue(pose1.position is not pose2.position)
        self.assertTrue(pose1.orientation is not pose2.orientation)

        pose1 = Pose(Position(1, 1), 1 + 2*m.pi)
        self.assertAlmostEqual(pose1.orientation, 1)
        pose2 = Pose(pose1)
        self.assertAlmostEqual(pose2.orientation, 1)

        #  From a size 3 numpy array
        my_array = np.array([1, 1, np.pi/4])
        pose = Pose(my_array)
        self.assertEqual(pose.position, Position(1, 1))
        self.assertEqual(pose.orientation, np.pi/4)
        my_array[0] = 2
        self.assertNotEqual(pose.position, Position(2, 1))
        self.assertTrue(pose.orientation is not my_array[2])

        my_array = np.array([1, 1, np.pi/4 + 2*np.pi])
        pose = Pose(my_array)
        self.assertEqual(pose.position, Position(1, 1))
        self.assertAlmostEqual(pose.orientation, np.pi/4)

        #  From positional arguments (Position(), orientation)
        my_position = Position(1, 2)
        pose = Pose(my_position, 3)
        self.assertEqual(pose.position, Position(1, 2))
        self.assertEqual(pose.orientation, 3)
        self.assertTrue(pose.position is not my_position)

        #  From positional arguments (x, y, orientation)
        pose = Pose(1, 2, 3)
        self.assertEqual(pose.position, Position(1, 2))
        self.assertEqual(pose.orientation, 3)

        pose = Pose(1, 2, 3 + 2*m.pi)
        self.assertAlmostEqual(pose.orientation, 3)

        #  From a size 2 numpy array and orientation (np.array, orientation)
        my_array = np.array([1, 2])
        pose = Pose(my_array)
        self.assertEqual(pose.position, Position(1, 2))
        self.assertEqual(pose.orientation, 0)
        my_array[0] = 2
        self.assertNotEqual(pose.position, Position(2, 2))

        my_array = np.array([1, 2])
        pose = Pose(my_array, 3)
        self.assertEqual(pose.position, Position(1, 2))
        self.assertEqual(pose.orientation, 3)
        my_array[0] = 2
        self.assertNotEqual(pose.position, Position(2, 2))

        my_array = np.array([1, 2])
        pose = Pose(my_array, 3 + 2*m.pi)
        self.assertAlmostEqual(pose.orientation, 3)

        #   Error cases

        with self.assertRaises(ValueError):
            Pose(0)
        with self.assertRaises(ValueError):
            Pose(0, 0, 0, 0)
        with self.assertRaises(ValueError):
            Pose({})
        with self.assertRaises(ValueError):
            Pose([])
        with self.assertRaises(ValueError):
            Pose([0])
        with self.assertRaises(ValueError):
            Pose([0], 0)
        with self.assertRaises(ValueError):
            Pose([0, 0, 0])
        with self.assertRaises(ValueError):
            Pose([0, 0, 0], 0)
        with self.assertRaises(ValueError):
            Pose(())
        with self.assertRaises(ValueError):
            Pose((), 0)
        with self.assertRaises(ValueError):
            Pose((0, 0, 0))
        with self.assertRaises(ValueError):
            Pose((0, 0, 0), 0)
        with self.assertRaises(ValueError):
            Pose(np.zeros(1))
        with self.assertRaises(ValueError):
            Pose(np.zeros(1), 0)
        with self.assertRaises(ValueError):
            Pose(np.zeros(4))
        with self.assertRaises(ValueError):
            Pose(np.zeros(4), 0)

    def test_get_set(self):
        pose = Pose(Position(1, 2), 3)

        self.assertTrue(hasattr(pose, 'position'))
        self.assertTrue(hasattr(pose, 'orientation'))

        self.assertTrue(pose.position == Position(1, 2))
        self.assertTrue(pose.orientation == 3)

        pose.position = Position(2, 3)
        pose.orientation = 1
        self.assertTrue(pose.position == Position(2, 3))
        self.assertTrue(pose.orientation == 1)

        self.assertEqual(pose[0], 2)
        self.assertEqual(pose[1], 3)
        self.assertEqual(pose[2], 1)
        with self.assertRaises(IndexError):
            pose[3]

    def test_add(self):
        pose1 = Pose(Position(1, 2), 3)
        pose2 = Pose(Position(5, 7), 9)
        pose3 = pose1 + pose2
        self.assertEqual(pose3.position, Position(6, 9))
        self.assertEqual(pose3.orientation, 12 - 4*m.pi)

        pos = Position(10, 20)
        pose4 = pose1 + pos
        self.assertEqual(pose4.position, Position(11, 22))
        self.assertEqual(pose4.orientation, 3)

        with self.assertRaises(TypeError):
            pos + pose1

    def test_sub(self):
        pose1 = Pose(Position(1, 2), 3)
        pose2 = Pose(Position(5, 7), 9)
        pose3 = pose1 - pose2
        self.assertEqual(pose3.position, Position(-4, -5))
        self.assertEqual(pose3.orientation, -6 + 2*m.pi)

        pos = Position(10, 20)
        pose4 = pose1 - pos
        self.assertEqual(pose4.position, Position(-9, -18))
        self.assertEqual(pose4.orientation, 3)

        with self.assertRaises(TypeError):
            pos - pose1

    def test_eq(self):
        self.assertEqual(Pose(), Pose())

        from Util import ORIENTATION_ABSOLUTE_TOLERANCE
        tol = 0.9999 * ORIENTATION_ABSOLUTE_TOLERANCE

        self.assertEqual(Pose(Position(), 1), Pose(Position(), 1 + tol))
        self.assertEqual(Pose(Position(), 1), Pose(Position(), 1 - tol))
        self.assertNotEqual(Pose(Position(), 1), Pose(Position(), 1 + 1.1*tol))
        self.assertNotEqual(Pose(Position(), 1), Pose(Position(), 1 - 1.1*tol))

        self.assertEqual(Pose(Position(), 0), Pose(Position(), +tol))
        self.assertEqual(Pose(Position(), 0), Pose(Position(), -tol))
        self.assertEqual(Pose(Position(), +tol), Pose(Position(), 0))
        self.assertEqual(Pose(Position(), -tol), Pose(Position(), 0))
        self.assertNotEqual(Pose(Position(), 0), Pose(Position(), +1.1*tol))
        self.assertNotEqual(Pose(Position(), 0), Pose(Position(), -1.1*tol))
        self.assertNotEqual(Pose(Position(), +1.1*tol), Pose(Position(), 0))
        self.assertNotEqual(Pose(Position(), -1.1*tol), Pose(Position(), 0))

        self.assertEqual(Pose(Position(), 0), Pose(Position(), 2*m.pi + tol))
        self.assertEqual(Pose(Position(), 0), Pose(Position(), 2*m.pi - tol))
        self.assertNotEqual(Pose(Position(), 0), Pose(Position(), 2*m.pi + 1.1*tol))
        self.assertNotEqual(Pose(Position(), 0), Pose(Position(), 2*m.pi - 1.1*tol))

        self.assertEqual(Pose(Position(), m.pi), Pose(Position(), -m.pi))
        self.assertEqual(Pose(Position(), m.pi+tol), Pose(Position(), -m.pi))
        self.assertEqual(Pose(Position(), m.pi), Pose(Position(), -m.pi+tol))
        self.assertEqual(Pose(Position(), m.pi-tol), Pose(Position(), -m.pi))
        self.assertEqual(Pose(Position(), m.pi), Pose(Position(), -m.pi - tol))

        self.assertNotEqual(Pose(Position(), m.pi+1.1*tol), Pose(Position(), -m.pi))
        self.assertNotEqual(Pose(Position(), m.pi), Pose(Position(), -m.pi+1.1*tol))
        self.assertNotEqual(Pose(Position(), m.pi-1.1*tol), Pose(Position(), -m.pi))
        self.assertNotEqual(Pose(Position(), m.pi), Pose(Position(), -m.pi-1.1*tol))

    def test_wrap_to_pi(self):
        self.assertEqual(Pose.wrap_to_pi(0), 0)
        self.assertEqual(Pose.wrap_to_pi(-1), -1)
        self.assertEqual(Pose.wrap_to_pi(1), 1)
        self.assertEqual(Pose.wrap_to_pi(m.pi), -m.pi)
        self.assertEqual(Pose.wrap_to_pi(-m.pi), -m.pi)
        self.assertEqual(Pose.wrap_to_pi(2 * m.pi), 0)

    def test_compare_orientation(self):
        #  numeric input
        pose = Pose(Position(), 0)
        self.assertTrue(pose.compare_orientation(0))
        tol = 0.01
        self.assertTrue(pose.compare_orientation(0.00399, tol))
        self.assertTrue(pose.compare_orientation(-0.00399, tol))
        pose.orientation = m.pi
        self.assertTrue(pose.compare_orientation(m.pi))
        self.assertTrue(pose.compare_orientation(-m.pi))
        tol = 0.01
        self.assertTrue(pose.compare_orientation(m.pi+0.999*tol, tol))
        self.assertTrue(pose.compare_orientation(-m.pi-0.999*tol, tol))
        self.assertTrue(pose.compare_orientation(m.pi-0.999*tol, tol))
        self.assertTrue(pose.compare_orientation(-m.pi+0.999*tol, tol))
        self.assertFalse(pose.compare_orientation(m.pi+1.001*tol, tol))
        self.assertFalse(pose.compare_orientation(-m.pi-1.001*tol, tol))
        self.assertFalse(pose.compare_orientation(m.pi-1.001*tol, tol))
        self.assertFalse(pose.compare_orientation(-m.pi+1.001*tol, tol))

        pose1 = Pose(Position(1, 1), 0)
        pose2 = Pose(Position(10, 10), 0)
        self.assertTrue(pose1.compare_orientation(pose2))

    def test_to_array(self):
        pose = Pose(Position(1, 2), 3)
        pose_array = pose.to_array()
        self.assertEqual(pose_array[0], 1)
        self.assertEqual(pose_array[1], 2)
        self.assertEqual(pose_array[2], 3)
        self.assertTrue(type(pose_array) is np.ndarray)

    def test_to_tuple(self):
        uut = Pose()
        #sanity check
        self.assertNotEqual(type(uut.to_tuple()), type(Pose()))
        self.assertEqual(type(uut.to_tuple()), type(tuple()))

        self.assertEqual(uut.to_tuple(), tuple((0, 0)))

        uut = Pose(Position(557, -778.5), 0)
        self.assertEqual(uut.to_tuple(), tuple((557, -778.5)))
        self.assertNotEqual(uut.to_tuple(), tuple((-42, 3897)))
